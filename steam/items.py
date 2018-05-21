"""
Steam economy - Inventories, schemas, assets, etc.
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

import time
import operator
from . import api, loc


class SchemaError(api.APIError):
    pass


class AssetError(api.APIError):
    pass


class InventoryError(api.APIError):
    pass


class BadID64Error(InventoryError):
    pass


class ProfilePrivateError(InventoryError):
    pass


class schema(object):
    """ Wrapper for item schema of certain games from Valve. Those are currently
    available (along with their ids):

        * ``260`` - Counter Strike: Source Beta
        * ``440`` - Team Fortress 2
        * ``520`` - Team Fortress 2 Public Beta
        * ``570`` - Dota 2
        * ``620`` - Portal 2
        * ``710`` - Counter-Strike: Global Offensive Beta Dev
        * ``816`` - Dota 2 internal test
        * ``841`` - Portal 2 Beta
        * ``205790`` - Dota 2 (beta) test
    """

    @property
    def _schema(self):
        if self._cache:
            return self._cache

        try:
            status = self._api["result"]["status"]

            # Client schema URL
            self._cache["client"] = self._api["result"]["items_game_url"]

            # ID:name origin map
            onames = self._api["result"].get("originNames", [])
            self._cache["origins"] = dict([(o["origin"], o["name"]) for o in onames])

            # Two maps are built here, one for name:ID and one for ID:loc name.
            # Most of the time qualities will be resolved by ID (as that's what
            # they are in inventories, it's mostly just the schema that
            # specifies qualities by non-loc name)
            qualities = {}
            quality_names = {}
            for k, v in self._api["result"]["qualities"].items():
                locname = self._api["result"]["qualityNames"][k]
                idname = k.lower()
                qualities[v] = (v, idname, locname)
                quality_names[idname] = v
            self._cache["qualities"] = qualities
            self._cache["quality_names"] = quality_names

            # Two maps are built here, one for name:ID and one for
            # ID:attribute. As with qualities it's mostly the schema that needs
            # this extra layer of mapping. Inventories specify attribute IDs
            # and quality IDs alike directly.
            attributes = {}
            attribute_names = {}
            for attrib in self._api["result"]["attributes"]:
                attrid = attrib["defindex"]
                attributes[attrid] = attrib
                attribute_names[attrib["name"].lower()] = attrid
            self._cache["attributes"] = attributes
            self._cache["attribute_names"] = attribute_names

            # ID:system particle map
            particles = self._api["result"].get("attribute_controlled_attached_particles", [])
            self._cache["particles"] = dict([(p["id"], p) for p in particles])

            # Name:level eater rank map
            levels = self._api["result"].get("item_levels", [])
            self._cache["eater_ranks"] = dict([(l["name"], l["levels"]) for l in levels])

            # Type ID:Type eater score count types
            killtypes = self._api["result"].get("kill_eater_score_types", [])
            self._cache["eater_types"] = dict([(k["type"], k) for k in killtypes])

            # Schema ID:item map (building this is insanely fast, overhead is
            # minimal compared to lookup benefits in backpacks)
            if self._items is not None:
                items = self._items
            else:
                items = self._api["result"]["items"]
            self._cache["items"] = dict([(i["defindex"], i) for i in items])
        except KeyError:
            # Due to the various fields needed we can't check for certain
            # fields and fall back ala 'inventory'
            if status is not None:
                raise SchemaError("Steam returned bad schema with error code "
                                  + str(status))
            else:
                raise SchemaError("Empty or corrupt schema returned")

        return self._cache

    @property
    def client_url(self):
        """ Client schema URL """
        return self._schema["client"]

    @property
    def language(self):
        """ The ISO code of the language the instance
        is localized to """
        return self._language

    def _attribute_definition(self, attrid):
        """ Returns the attribute definition dict of a given attribute
        ID, can be the name or the integer ID """
        attrs = self._schema["attributes"]

        try:
            # Make a new dict to avoid side effects
            return dict(attrs[attrid])
        except KeyError:
            attr_names = self._schema["attribute_names"]
            attrdef = attrs.get(attr_names.get(str(attrid).lower()))

            if not attrdef:
                return None
            else:
                return dict(attrdef)

    def _quality_definition(self, qid):
        """ Returns the ID and localized name of the given quality, can be either ID type """
        qualities = self._schema["qualities"]

        try:
            return qualities[qid]
        except KeyError:
            qid = self._schema["quality_names"].get(str(qid).lower(), 0)
            return qualities.get(qid, (qid, "normal", "Normal"))

    @property
    def attributes(self):
        """ Returns all attributes in the schema """
        attrs = self._schema["attributes"]
        return [item_attribute(attr) for attr in sorted(attrs.values(),
                key=operator.itemgetter("defindex"))]

    @property
    def origins(self):
        """ Returns a map of all origins """
        return self._schema["origins"]

    @property
    def qualities(self):
        """
        Returns a dict of all possible qualities. The key(s) will be the ID,
        values are a tuple containing ID, name, localized name. To resolve
        a quality to a name intelligently use '_quality_definition'
        """
        return self._schema["qualities"]

    @property
    def particle_systems(self):
        """ Returns a dictionary of particle system dicts keyed by ID """
        return self._schema["particles"]

    @property
    def kill_ranks(self):
        """ Returns a list of ranks for weapons with kill tracking """
        return self._schema["eater_ranks"]

    @property
    def kill_types(self):
        """ Returns a dict with keys that are the value of
        the kill eater type attribute and values that are the name
        string """
        return self._schema["eater_types"]

    def origin_id_to_name(self, origin):
        """ Returns a localized origin name for a given ID """
        try:
            oid = int(origin)
        except (ValueError, TypeError):
            return None

        return self.origins.get(oid)

    def _find_item_by_id(self, id):
        return self._schema["items"].get(id)

    def __iter__(self):
        return next(self)

    def __next__(self):
        iterindex = 0
        iterdata = list(self._schema["items"].values())

        while(iterindex < len(iterdata)):
            data = item(iterdata[iterindex], self)
            iterindex += 1
            yield data
    next = __next__

    def __getitem__(self, key):
        realkey = None
        try:
            realkey = key["defindex"]
        except:
            realkey = key

        schema_item = self._find_item_by_id(realkey)
        if schema_item:
            return item(schema_item, self)
        else:
            raise KeyError(key)

    def __len__(self):
        return len(self._schema["items"])

    def __init__(self, app, lang=None, version=1, **kwargs):
        """ schema will be used to initialize the schema if given,
        lang can be any ISO language code.
        lm will be used to generate an HTTP If-Modified-Since header. """

        self._language = loc.language(lang).code
        self._app = int(app)
        self._cache = {}

        # WORKAROUND: CS GO v1 returns 404
        if self._app == 730 and version == 1:
            version = 2

        # WORKAROUND: certain apps have moved to GetSchemaOverview/GetSchemaItems
        if self._app in [440]:
            self._api = api.interface("IEconItems_" + str(self._app)).GetSchemaOverview(language=self._language, version=version, **kwargs)
            items = []
            next_start = 0
            # HACK: build the entire item list immediately because Valve decided not to allow us to get the entire thing at once
            while next_start is not None:
                next_items = api.interface("IEconItems_" + str(self._app)).GetSchemaItems(language=self._language, version=version, aggressive=True, start=next_start, **kwargs)
                items.extend(next_items["result"]["items"])
                next_start = next_items["result"].get("next", None)
            self._items = items
        else:
            self._api = api.interface("IEconItems_" + str(self._app)).GetSchema(language=self._language, version=version, **kwargs)
            self._items = None


class item(object):
    """ Stores a single inventory item. """

    @property
    def attributes(self):
        """ Returns a list of attributes """

        overridden_attrs = self._attributes
        sortmap = {"neutral": 1, "positive": 2,
                   "negative": 3}

        sortedattrs = list(overridden_attrs.values())
        sortedattrs.sort(key=operator.itemgetter("defindex"))
        sortedattrs.sort(key=lambda t: sortmap.get(t.get("effect_type",
                                                         "neutral"), 99))
        return [item_attribute(theattr) for theattr in sortedattrs]

    @property
    def quality(self):
        """ Returns a tuple containing ID, name, and localized name of the quality """
        return self._quality

    @property
    def inventory_token(self):
        """ Returns the item's inventory token (a bitfield),
        deprecated. """
        return self._item.get("inventory", 0)

    @property
    def position(self):
        """ Returns a position in the inventory or -1 if there's no position
        available (i.e. an item hasn't dropped yet or got displaced) """

        inventory_token = self.inventory_token

        if inventory_token == 0:
            return -1
        else:
            return inventory_token & 0xFFFF

    @property
    def equipped(self):
        """ Returns a dict of classes that have the item equipped and in what slot """
        equipped = self._item.get("equipped", [])

        # WORKAROUND: 0 is probably an off-by-one error
        # WORKAROUND: 65535 actually serves a purpose (according to Valve)
        return dict([(eq["class"], eq["slot"]) for eq in equipped if eq["class"] != 0 and eq["slot"] != 65535])

    @property
    def equipable_classes(self):
        """ Returns a list of classes that _can_ use the item. """
        sitem = self._schema_item

        return [c for c in sitem.get("used_by_classes", self.equipped.keys()) if c]

    @property
    def schema_id(self):
        """ Returns the item's ID in the schema. """
        return self._item["defindex"]

    @property
    def name(self):
        """ Returns the item's undecorated name """
        return self._schema_item.get("item_name", str(self.id))

    @property
    def type(self):
        """ Returns the item's type. e.g. "Kukri" for the Tribalman's Shiv.
        If Valve failed to provide a translation the type will be the token without
        the hash prefix. """
        return self._schema_item.get("item_type_name", '')

    @property
    def icon(self):
        """ URL to a small thumbnail sized image of the item, suitable for display in groups """
        return self._schema_item.get("image_url", '')

    @property
    def image(self):
        """ URL to a full sized image of the item, for displaying 'zoomed-in' previews """
        return self._schema_item.get("image_url_large", '')

    @property
    def id(self):
        """ Returns the item's unique serial number if it has one """
        return self._item.get("id")

    @property
    def original_id(self):
        """ Returns the item's original ID if it has one. This is the last "version"
        of the item before it was customized or otherwise changed """
        return self._item.get("original_id")

    @property
    def level(self):
        """ Returns the item's level (e.g. 10 for The Axtinguisher) if it has one """
        return self._item.get("level")

    @property
    def slot_name(self):
        """ Returns the item's slot as a string, this includes "primary",
        "secondary", "melee", and "head". Note that this is the slot
        of the item as it appears in the schema, and not necessarily
        the actual equipable slot. (see 'equipped')"""
        return self._schema_item.get("item_slot")

    @property
    def cvar_class(self):
        """ Returns the item's class
        (what you use in the game to equip it, not the craft class)"""
        return self._schema_item.get("item_class")

    @property
    def craft_class(self):
        """ Returns the item's class in the crafting system if it has one.
        This includes hat, craft_bar, or craft_token. """
        return self._schema_item.get("craft_class")

    @property
    def craft_material_type(self):
        return self._schema_item.get("craft_material_type")

    @property
    def custom_name(self):
        """ Returns the item's custom name if it has one. """
        return self._item.get("custom_name")

    @property
    def custom_description(self):
        """ Returns the item's custom description if it has one. """
        return self._item.get("custom_desc")

    @property
    def quantity(self):
        """ Returns the number of uses the item has,
        for example, a dueling mini-game has 5 uses by default """
        return self._item.get("quantity", 1)

    @property
    def description(self):
        """ Returns the item's default description if it has one """
        return self._schema_item.get("item_description")

    @property
    def min_level(self):
        """ Returns the item's minimum level
        (non-random levels will have the same min and max level) """
        return self._schema_item.get("min_ilevel")

    @property
    def max_level(self):
        """ Returns the item's maximum level
        (non-random levels will have the same min and max level) """
        return self._schema_item.get("max_ilevel")

    @property
    def contents(self):
        """ Returns the item in the container, if there is one.
        This will be a standard item object. """
        rawitem = self._item.get("contained_item")
        if rawitem:
            return self.__class__(rawitem, self._schema)

    @property
    def tradable(self):
        """ Somewhat of a WORKAROUND since this flag is there
        sometimes, "cannot trade" is there sometimes
        and then there's "always tradable". Opposed to
        only occasionally tradable when it feels like it.
        Attr 153 = cannot trade """
        return not (self._item.get("flag_cannot_trade") or (153 in self))

    @property
    def craftable(self):
        """ Returns not craftable if the cannot craft flag exists. True, otherwise. """
        return not self._item.get("flag_cannot_craft")

    @property
    def full_name(self):
        """
        The full  name of the item, generated depending
        on things such as its quality, rank, the schema language,
        and so on.
        """
        qid, quality_str, pretty_quality_str = self.quality
        custom_name = self.custom_name
        item_name = self.name
        english = (self._language == "en_US")
        rank = self.rank
        prefixed = self._schema_item.get("proper_name", False)
        prefix = ''
        suffix = ''
        pfinal = ''

        if item_name.startswith("The ") and prefixed:
            item_name = item_name[4:]

        if quality_str != "unique" and quality_str != "normal":
            pfinal = pretty_quality_str

        if english:
            if prefixed:
                if quality_str == "unique":
                    pfinal = "The"
            elif quality_str == "unique":
                pfinal = ''

        if rank and quality_str == "strange":
            pfinal = rank["name"]

        if english:
            prefix = pfinal
        elif pfinal:
            suffix = '(' + pfinal + ') ' + suffix

        return (prefix + " " + item_name + " " + suffix).strip()

    @property
    def kill_eaters(self):
        """
        Returns a list of tuples containing the proper localized kill eater type strings and their values
        according to set/type/value "order"
        """

        eaters = {}
        ranktypes = self._kill_types

        for attr in self:
            aname = attr.name.strip()
            aid = attr.id

            if aname.startswith("kill eater"):
                try:
                    # Get the name prefix (matches up type and score and
                    # determines the primary type for ranking)
                    eateri = list(filter(None, aname.split(' ')))[-1]
                    if eateri.isdigit():
                        eateri = int(eateri)
                    else:
                        # Probably the primary type/score which has no number
                        eateri = 0
                except IndexError:
                    # Fallback to attr ID (will completely fail to make
                    # anything legible but better than nothing)
                    eateri = aid

                if aname.find("user") != -1:
                    # User score types have lower sorting priority
                    eateri += 100

                eaters.setdefault(eateri, [None, None])
                if aname.find("score type") != -1 or aname.find("kill type") != -1:
                    # Score type attribute
                    if eaters[eateri][0] is None:
                        eaters[eateri][0] = attr.value
                else:
                    # Value attribute
                    eaters[eateri][1] = attr.value

        eaterlist = []
        defaultleveldata = "KillEaterRank"
        for key, eater in sorted(eaters.items()):
            etype, count = eater

            # Eater type can be null (it still is in some older items), null
            # count means we're looking at either an uninitialized item or
            # schema item
            if count is not None:
                rank = ranktypes.get(etype or 0,
                                     {"level_data": defaultleveldata,
                                      "type_name": "Count"})
                eaterlist.append((rank.get("level_data", defaultleveldata),
                                  rank["type_name"], count))

        return eaterlist

    @property
    def rank(self):
        """
        Returns the item's rank (if it has one)
        as a dict that includes required score, name, and level.
        """

        if self._rank != {}:
            # Don't bother doing attribute lookups again
            return self._rank

        try:
            # The eater determining the rank
            levelkey, typename, count = self.kill_eaters[0]
        except IndexError:
            # Apparently no eater available
            self._rank = None
            return None

        rankset = self._ranks.get(levelkey,
                                  [{"level": 0,
                                    "required_score": 0,
                                    "name": "Strange"}])

        for rank in rankset:
            self._rank = rank
            if count < rank["required_score"]:
                break

        return self._rank

    @property
    def available_styles(self):
        """ Returns a list of all styles defined for the item """
        styles = self._schema_item.get("styles", [])

        return list(map(operator.itemgetter("name"), styles))

    @property
    def style(self):
        """ The current style the item is set to or None if the item has no styles """
        try:
            return self.available_styles[self._item.get("style", 0)]
        except IndexError:
            return None

    @property
    def capabilities(self):
        """ Returns a list of capabilities, these are flags for what the item can do or be done with """
        return list(self._schema_item.get("capabilities", {}).keys())

    @property
    def tool_metadata(self):
        """ A dict containing item dependant metadata such as holiday restrictions, types, and properties used by the client. Do not assume a stable syntax. """
        return self._schema_item.get("tool")

    @property
    def origin(self):
        """ Returns the item's localized origin name """
        return self._origin

    def __iter__(self):
        return next(self)

    def __next__(self):
        iterindex = 0
        attrs = self.attributes

        while(iterindex < len(attrs)):
            data = attrs[iterindex]
            iterindex += 1
            yield data
    next = __next__

    def __getitem__(self, key):
        for attr in self:
            if attr.id == key or attr.name == key:
                return attr

        raise KeyError(key)

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __str__(self):
        cname = self.custom_name
        fullname = self.full_name

        if cname:
            return "{0} ({1})".format(cname, fullname)
        else:
            return fullname

    def __init__(self, item, schema=None):
        self._item = item
        self._schema_item = None
        self._schema = schema
        self._rank = {}
        self._ranks = {}
        self._kill_types = {}
        self._origin = None
        self._attributes = {}

        if schema:
            self._schema_item = schema._find_item_by_id(self._item["defindex"])

        if not self._schema_item:
            self._schema_item = self._item

        qualityid = self._item.get("quality",
                                   self._schema_item.get("item_quality", 0))
        if schema:
            self._quality = schema._quality_definition(qualityid)
        else:
            self._quality = (qualityid, "normal", "Normal")

        if schema:
            self._language = schema.language
        else:
            self._language = "en_US"

        originid = self._item.get("origin")
        if schema:
            self._origin = schema.origin_id_to_name(originid)
        elif originid:
            self._origin = str(originid)

        if schema:
            self._ranks = schema.kill_ranks
            self._kill_types = schema.kill_types

        for attr in self._schema_item.get("attributes", []):
            index = attr.get("defindex", attr.get("name"))
            attrdef = None

            if schema:
                attrdef = schema._attribute_definition(index)
                if attrdef:
                    index = attrdef["defindex"]

            self._attributes.setdefault(index, {})

            if attrdef:
                self._attributes[index].update(attrdef)

            self._attributes[index].update(attr)

        if self._item != self._schema_item:
            for attr in self._item.get("attributes", []):
                index = attr["defindex"]

                if schema and index not in self._attributes:
                    attrdef = schema._attribute_definition(index)

                    if attrdef:
                        self._attributes[index] = attrdef

                self._attributes.setdefault(index, {})
                self._attributes[index].update(attr)


class item_attribute(object):
    """ Wrapper around item attributes. """

    @property
    def formatted_value(self):
        """ Returns a formatted value as a string"""
        # TODO: Cleanup all of this, it's just weird and unnatural maths
        val = self.value
        pval = val
        ftype = self.value_type

        if ftype == "percentage":
            pval = int(round(val * 100))

            if self.type == "negative":
                pval = 0 - (100 - pval)
            else:
                pval -= 100
        elif ftype == "additive_percentage":
            pval = int(round(val * 100))
        elif ftype == "inverted_percentage":
            pval = 100 - int(round(val * 100))

            # Can't remember what workaround this was, is it needed?
            if self.type == "negative":
                if self.value > 1:
                    pval = 0 - pval
        elif ftype == "additive" or ftype == "particle_index" or ftype == "account_id":
            if int(val) == val:
                pval = int(val)
        elif ftype == "date":
            d = time.gmtime(int(val))
            pval = time.strftime("%Y-%m-%d %H:%M:%S", d)

        return u"{0}".format(pval)

    @property
    def formatted_description(self):
        """ Returns a formatted description string (%s* tokens replaced) or None if unavailable """
        desc = self.description

        if desc:
            return desc.replace("%s1", self.formatted_value)
        else:
            return None

    @property
    def name(self):
        """ The attribute's name """
        return self._attribute.get("name", str(self.id))

    @property
    def cvar_class(self):
        """ The attribute class, mostly non-useful except for console usage in some cases """
        return self._attribute.get("attribute_class")

    @property
    def id(self):
        """ The attribute ID, used for indexing the description blocks in the schema """
        # I'm basically making a pun here, Esky, when you find this. Someday.
        # You owe me a dollar.
        return self._attribute.get("defindex", id(self))

    @property
    def type(self):
        """ Returns the attribute effect type (positive, negative, or neutral). This is not the same as the value type, see 'value_type' """
        return self._attribute.get("effect_type")

    @property
    def value(self):
        """
        Tries to intelligently return the raw value based on schema data.
        See also: 'value_int' and 'value_float'
        """
        # TODO: No way to determine which value to use without schema,
        # could be problem
        if self._isint:
            return self.value_int
        else:
            return self.value_float

    @property
    def value_int(self):
        try:
            # This is weird, I know, but so is Valve.
            # They store floats in value fields sometimes, sometimes not.
            # Oh and they also store strings in there too now!
            val = self._attribute.get("value", 0)

            if not isinstance(val, float):
                return int(val)
            else:
                return float(val)
        except ValueError:
            return 0

    @property
    def value_float(self):
        try:
            return float(self._attribute.get("float_value", self.value_int))
        except ValueError:
            return 0.0

    @property
    def description(self):
        """ Returns the attribute's description string, if
        it is intended to be printed with the value there will
        be a "%s1" token somewhere in the string. Use
        'formatted_description' to build one automatically. """
        return self._attribute.get("description_string")

    @property
    def value_type(self):
        """ The attribute's type, note that this is the type of the attribute's
        value and not its affect on the item (i.e. negative or positive). See
        'type' for that. """
        redundantprefix = "value_is_"
        vtype = self._attribute.get("description_format")

        if vtype and vtype.startswith(redundantprefix):
            return vtype[len(redundantprefix):]
        else:
            return vtype

    @property
    def hidden(self):
        """ True if the attribute is "hidden"
        (not intended to be shown to the end user). Note
        that hidden attributes also usually have no description string """
        return self._attribute.get("hidden", False) or self.description is None

    @property
    def account_info(self):
        """ Certain attributes have a user's account information
        associated with it such as a gifted or crafted item.

        A dict with two keys: 'persona' and 'id64'.
        None if the attribute has no account information attached to it. """
        account_info = self._attribute.get("account_info")
        if account_info:
            return {"persona": account_info.get("personaname", ""),
                    "id64": account_info["steamid"]}
        else:
            return None

    def __str__(self):
        """ Pretty printing """
        if not self.hidden:
            return self.formatted_description
        else:
            return self.name + ": " + self.formatted_value

    def __init__(self, attribute):
        self._attribute = attribute
        self._isint = self._attribute.get("stored_as_integer", False)


class inventory(object):
    """ Wrapper around player inventory. """

    @property
    def _inv(self):
        if self._cache:
            return self._cache

        status = None

        try:
            status = self._api["result"]["status"]
            items = self._api["result"]["items"]
        except KeyError:
            # Only try to check status code if items don't exist (why error out
            # when items are there)
            if status is not None:
                if status == 8:
                    raise BadID64Error("Bad Steam ID64 given")
                elif status == 15:
                    raise ProfilePrivateError("Profile is private")
            raise InventoryError("Backpack data incomplete or corrupt")

        self._cache = {
                "items": items,
                "cells": self._api["result"].get("num_backpack_slots", len(items))
                }

        return self._cache

    @property
    def cells_total(self):
        """ The total number of cells in the inventory.
        This can be used to determine if the user has bought an
        expander. This is NOT the number of items in the inventory, but
        how many items CAN be stored in it. The actual current inventory size
        can be obtained by calling len on an inventory object """
        return self._inv["cells"]

    def __getitem__(self, key):
        key = str(key)
        for item in self:
            if str(item.id) == key or str(item.original_id) == key:
                return item
        raise KeyError(key)

    def __iter__(self):
        return next(self)

    def __len__(self):
        return len(self._inv["items"])

    def __next__(self):
        iterindex = 0
        iterdata = self._inv["items"]

        while(iterindex < len(iterdata)):
            data = item(iterdata[iterindex], self._schema)
            iterindex += 1
            yield data
    next = __next__

    def __init__(self, app, profile, schema=None, **kwargs):
        """
        'app': Steam app to get the inventory for.
        'profile': A user ID or profile object.
        'schema': The schema to use for item lookup.
        """

        self._app = app
        self._schema = schema
        self._cache = {}

        try:
            sid = profile.id64
        except:
            sid = str(profile)

        self._api = api.interface("IEconItems_" + str(self._app)).GetPlayerItems(SteamID=sid, **kwargs)


class asset_item:
    """ Stores a single item from a steam asset catalog """

    def __init__(self, asset, catalog):
        self._catalog = catalog
        self._asset = asset

    def __str__(self):
        return self.name + " " + str(self.price)

    def _calculate_price(self, base=False):
        asset = self._asset
        pricemap = asset["prices"]

        if base:
            pricemap = asset.get("original_prices", pricemap)

        return dict([(currency, float(price) / 100) for currency, price in pricemap.items()])

    @property
    def tags(self):
        """ Returns a dict containing tags and their localized labels as values """
        return dict([(t, self._catalog.tags.get(t, t)) for t in self._asset.get("tags", [])])

    @property
    def base_price(self):
        """ The price the item normally goes for, not including discounts. """
        return self._calculate_price(base=True)

    @property
    def price(self):
        """ Returns the most current price available, which may include sales/discounts """
        return self._calculate_price(base = False)

    @property
    def name(self):
        """ The asset "name" which is in fact a schema id of item. """
        return self._asset.get("name")


class assets(object):
    """ Class for building asset catalogs """

    @property
    def _assets(self):
        if self._cache:
            return self._cache

        try:
            assets = dict([(asset["name"], asset) for asset in self._api["result"]["assets"]])
            tags = self._api["result"].get("tags", {})
        except KeyError:
            raise AssetError("Empty or corrupt asset catalog")

        self._cache = {
                "items": assets,
                "tags": tags
                }

        return self._cache

    @property
    def tags(self):
        """ Returns a dict that is a map of the internal tag names
        for this catalog to the localized labels. """

        return self._assets["tags"]

    def __contains__(self, key):
        """ Returns a whether a given asset ID exists within this
        catalog or not. """
        try:
            key = key.schema_id
        except AttributeError:
            pass

        return str(key) in self._assets["items"]

    def __getitem__(self, key):
        """ Returns an 'asset_item' for a given asset ID """
        assets = self._assets["items"]

        try:
            key = key.schema_id
        except AttributeError:
            pass

        return asset_item(assets[str(key)], self)

    def __iter__(self):
        return next(self)

    def __next__(self):
        # This was previously sorted, but I don't think order matters here.
        # Does it?
        data = list(self._assets["items"].values())
        iterindex = 0

        while iterindex < len(data):
            ydata = asset_item(data[iterindex], self)
            iterindex += 1
            yield ydata
    next = __next__

    def __init__(self, app, lang=None, **kwargs):
        """ lang: Language of asset tags, defaults to english
        currency: The iso 4217 currency code, returns all currencies by default """

        self._language = loc.language(lang).code
        self._app = app
        self._cache = {}

        self._api = api.interface("ISteamEconomy").GetAssetPrices(language=self._language, appid=self._app, **kwargs)
