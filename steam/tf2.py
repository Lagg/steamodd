"""
Module for reading Team Fortress 2 data using the Steam API

Copyright (c) 2010, Anthony Garcia <lagg@lavabit.com>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import json, os, urllib2, time, steam

class TF2Error(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return str(self.msg)

class SchemaError(TF2Error):
    def __init__(self, msg, status = 0):
        TF2Error.__init__(self, msg)
        self.msg = msg

class ItemError(TF2Error):
    def __init__(self, msg, item = None):
        TF2Error.__init__(self, msg)
        self.msg = msg
        self.item = item

class item_schema:
    """ The base class for the item schema. """

    def get_language(self):
        """ Returns the ISO code of the language the instance
        is localized to """
        return self._language

    def get_raw_attributes(self, item = None):
        """ Returns all attributes in the schema or for the item if one is given """

        dabiglist = self._schema["result"]["attributes"]["attribute"] or []
        attrs = []
        realattrs = []
        if not item:
            return dabiglist

        for sitem in self._schema["result"]["items"]["item"]:
            if sitem["defindex"] == item._item["defindex"]:
                try: attrs = sitem["attributes"]["attribute"]
                except KeyError: attrs = []
                break

        for specattr in attrs:
            for attr in dabiglist:
                if specattr["name"] == attr["name"]:
                    realattrs.append(dict(attr.items() + specattr.items()))

        return realattrs

    def get_attributes(self, item = None):
        """ Returns all attributes in the schema
        or the attributes for the item if given"""

        return [item_attribute(attr) for attr in self.get_raw_attributes(item)]

    def get_qualities(self):
        """ Returns a list of all possible item qualities,
        each element will be a dict.
        prettystr is the localized pretty name (e.g. Valve)
        id is the numerical quality (e.g. 8)
        str is the non-pretty string (e.g. developer) """

        qualities = []

        for k,v in self._schema["result"]["qualities"].iteritems():
            aquality = {"id": v, "str": k, "prettystr": k}

            try: aquality["prettystr"] = self._schema["result"]["qualityNames"][aquality["str"]]
            except KeyError: pass

            qualities.append(aquality)

        return qualities

    def _download(self, lang):
        url = ("http://api.steampowered.com/ITFItems_440/GetSchema/v0001/?key=" +
               steam.get_api_key() + "&format=json&language=" + lang)
        self._language = lang

        return json.load(urllib2.urlopen(url))

    def __iter__(self):
        return self.nextitem()

    def nextitem(self):
        iterindex = 0
        iterdata = self._schema["result"]["items"]["item"]

        while(iterindex < len(iterdata)):
            data = item(self, iterdata[iterindex])
            iterindex += 1
            yield data

    def __getitem__(self, key):
        realkey = None
        try: realkey = key["defindex"]
        except: realkey = key

        for item in self:
            if realkey == item.get_schema_id():
                return item

        raise KeyError(key)

    def __init__(self, schema = None, lang = "en"):
        """ schema will be used to initialize the schema if given,
        lang can be any ISO language code. """

        if not schema:
            try:
                self._schema = self._download(lang)
            except urllib2.URLError:
                # Try once more
                self._schema = self._download(lang)
            except Exception as E:
                raise SchemaError(E)

            if not self._schema or self._schema["result"]["status"] != 1:
                raise SchemaError("Schema error", self._schema["result"]["status"])
        else:
            self._schema = schema

class item:
    """ Stores a single TF2 backpack item """
    # The bitfield in the inventory token where
    # equipped classes are stored
    equipped_field = 0x1FF0000

    # A list of equipped classes and their position
    # in the inventory token
    equipped_classes = {
        1<<8: "Engineer",
        1<<7: "Spy",
        1<<6: "Pyro",
        1<<5: "Heavy",
        1<<4: "Medic",
        1<<3: "Demoman",
        1<<2: "Soldier",
        1<<1: "Sniper",
        1<<0: "Scout"
        }

    # Item image fields in the schema
    ITEM_IMAGE_SMALL = "image_url"
    ITEM_IMAGE_LARGE = "image_url_large"

    def get_attributes(self):
        """ Returns a list of attributes """

        schema_attrs = self._schema.get_raw_attributes(self)
        schema_block = self._schema.get_raw_attributes()
        item_attrs = []
        final_attrs = []

        if self._item != self._schema_item:
            try: item_attrs = self._item["attributes"]["attribute"]
            except KeyError: pass

        usedattrs = []
        for attr in schema_attrs:
            used = False
            for iattr in item_attrs:
                if attr["defindex"] == iattr["defindex"]:
                    final_attrs.append(dict(attr.items() + iattr.items()))
                    used = True
                    usedattrs.append(iattr)
                    break
            if not used:
                final_attrs.append(attr)

        for attr in item_attrs:
            if attr in usedattrs:
                continue
            for sattr in schema_block:
                if sattr["defindex"] == attr["defindex"]:
                    final_attrs.append(dict(sattr.items() + attr.items()))
                    break

        return [item_attribute(theattr) for theattr in final_attrs]

    def get_quality(self):
        """ Returns a dict
        prettystr is the localized pretty name (e.g. Valve)
        id is the numerical quality (e.g. 8)
        str is the non-pretty string (e.g. developer) """

        qid = 0
        item = self._item
        qid = item.get("quality", item.get("item_quality", 0))
        qualities = self._schema.get_qualities()

        for q in qualities:
            if q["id"] == qid:
                return q

        return {"id": 0, "prettystr": "Broken", "str": "ohnoes"}

    def get_inventory_token(self):
        """ Returns the item's inventory token (a bitfield) """
        return self._item.get("inventory", 0)

    def get_position(self):
        """ Returns a position in the backpack or -1 if there's no position
        available (i.e. an item isn't in the backpack) """

        inventory_token = self.get_inventory_token()

        if inventory_token == 0:
            return -1
        else:
            return inventory_token & 0xFFFF

    def get_equipped_classes(self):
        """ Returns a list of classes (see equipped_classes values) """
        classes = []

        inventory_token = self.get_inventory_token()

        for k,v in self.equipped_classes.iteritems():
            if ((inventory_token & self.equipped_field) >> 16) & k:
                classes.append(v)

        return classes

    def get_equipable_classes(self):
        """ Returns a list of classes that _can_ use the item. """
        classes = []
        sitem = self._schema_item

        try: classes = sitem["used_by_classes"]["class"]
        except KeyError: classes = self.equipped_classes.values()

        if len(classes) <= 0 or classes[0] == None: return []
        else: return classes

    def get_schema_id(self):
        """ Returns the item's ID in the schema. """
        return self._item["defindex"]

    def get_name(self):
        """ Returns the item's undecorated name """
        return self._schema_item["item_name"]

    def get_type(self):
        """ Returns the item's type. e.g. "Kukri" for the Tribalman's Shiv.
        If Valve failed to provide a translation the type will be the token without
        the hash prefix. """
        return self._schema_item["item_type_name"]

    def get_image(self, size):
        """ Returns the URL to the item's image, size should be one of
        ITEM_IMAGE_* """
        try:
            return self._schema_item[size]
        except KeyError:
            raise TF2Error("Bad item image size given")

    def get_id(self):
        """ Returns the item's unique serial number if it has one """
        return self._item.get("id")

    def get_level(self):
        """ Returns the item's level (e.g. 10 for The Axtinguisher) if it has one """
        return self._item.get("level")

    def get_slot(self):
        """ Returns the item's slot as a string, this includes "primary",
        "secondary", "melee", and "head" """
        return self._schema_item["item_slot"]

    def get_class(self):
        """ Returns the item's class
        (what you use in the console to equip it, not the craft class)"""
        return self._schema_item.get("item_class")

    def get_craft_class(self):
        """ Returns the item's class in the crafting system if it has one.
        This includes hat, craft_bar, or craft_token. """
        return self._schema_item.get("craft_class")

    def get_custom_name(self):
        """ Returns the item's custom name if it has one. """
        return self._item.get("custom_name")

    def get_custom_description(self):
        """ Returns the item's custom description if it has one. """
        return self._item.get("custom_desc")

    def get_quantity(self):
        """ Returns the number of uses the item has,
        for example, a dueling mini-game has 5 uses by default """
        return self._item.get("quantity", 1)

    def get_description(self):
        """ Returns the item's default description if it has one """
        return self._schema_item.get("item_description")

    def get_min_level(self):
        """ Returns the item's minimum level
        (non-random levels will have the same min and max level) """
        return self._schema_item.get("min_ilevel")

    def get_max_level(self):
        """ Returns the item's maximum level
        (non-random levels will have the same min and max level) """
        return self._schema_item.get("max_ilevel")

    def get_contents(self):
        """ Returns the item in the container, if there is one.
        This will be a standard item object. """
        rawitem = self._item.get("contained_item")
        if rawitem: return item(self._schema, rawitem)

    def is_untradable(self):
        """ Returns True if the item cannot be traded, False
        otherwise. """
        # Somewhat a WORKAROUND since this flag is there
        # sometimes, "cannot trade" is there somtimes
        # and then there's "always tradable". Opposed to
        # only occasionally tradable when it feels like it.
        untradable = self._item.get("flag_cannot_trade", False)
        if "cannot trade" in self:
            untradable = True
        if "always tradable" in self:
            untradable = False
        return untradable

    def is_name_prefixed(self):
        """ Returns False if the item doesn't use
        a prefix, True otherwise. (e.g. Bonk! Atomic Punch
        shouldn't have a prefix so this would be False) """
        return self._schema_item.get("proper_name", False)

    def get_full_item_name(self, strip_prefixes = [], prefixes = {}):
        """
        Generates a prefixed item name and is custom name-aware.

        Will use an alternate prefix dict if given,
        following the format of "non-localized quality": "alternate prefix"

        strip_prefixes is a list that will be checked for prefixes to remove
        from the item name, each element should be a non-localized quality string
        """
        quality = self.get_quality()
        quality_str = quality["str"]
        pretty_quality_str = quality["prettystr"]
        custom_name = self.get_custom_name()
        item_name = self.get_name()
        prefix = prefixes.get(quality_str, pretty_quality_str) + " "

        if item_name.find("The ") != -1 and self.is_name_prefixed():
            item_name = item_name[4:]

        if custom_name:
            item_name = custom_name

        if custom_name or not self.is_name_prefixed() or quality_str in strip_prefixes:
            return item_name
        else:
            return prefix + item_name

    def __iter__(self):
        return self.nextattr()

    def nextattr(self):
        iterindex = 0
        attrs = self.get_attributes()

        while(iterindex < len(attrs)):
            data = attrs[iterindex]
            iterindex += 1
            yield data

    def __getitem__(self, key):
        for attr in self:
            if attr.get_id() == key or attr.get_name() == key:
                return attr

        raise KeyError(key)

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __unicode__(self):
        return self.get_full_item_name()

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __init__(self, schema, item):
        self._item = item
        self._schema = schema
        self._schema_item = None

        # Assume it isn't a schema item if it doesn't have a name
        if "item_name" not in self._item:
            for sitem in schema._schema["result"]["items"]["item"]:
                if sitem["defindex"] == self._item["defindex"]:
                    self._schema_item = sitem
                    break
        else:
            self._schema_item = item

        if not self._schema_item:
            raise ItemError("Item has no corresponding schema entry")

class item_attribute:
    """ Wrapper around item attributes """

    def get_value_formatted(self, value = None):
        """ Returns a formatted value as a string"""
        if value == None:
            val = self.get_value()
        else:
            val = value
        fattr = str(val)
        ftype = self.get_value_type()

        # I don't think %s2,%s3, etc. needs to be supported since there's
        # 1 value per attribute.
        if ftype == "percentage" or ftype == "additive_percentage":
            intp = val
            if intp > 1: intp -= 1
            fattr = str(int(round(intp, 2) * 100))
        elif ftype == "inverted_percentage":
            fattr = str(100 - int(round(val, 2) * 100))
        elif ftype == "additive" or ftype == "particle_index" or ftype == "account_id":
            if int(val) == val: fattr = (str(int(val)))
        elif ftype == "date":
            d = time.gmtime(int(val))
            fattr = time.strftime("%F %H:%M:%S", d)

        return fattr

    def get_description_formatted(self):
        """ Returns a formatted description string (%s* tokens replaced) """
        val = self.get_value()
        ftype = self.get_value_type()
        desc = self.get_description()

        if desc:
            return desc.replace("%s1", self.get_value_formatted())
        else:
            return None

    def get_name(self):
        """ Returns the attributes name """
        return self._attribute["name"]

    def get_class(self):
        return self._attribute["attribute_class"]

    def get_id(self):
        return self._attribute["defindex"]

    def get_value_min(self):
        """ Returns the minimum value for the attribute (not all attributes
        stay above this) """
        return self._attribute["min_value"]

    def get_value_max(self):
        """ Returns the maximum value for the attribute (not all attributes
        stay below this) """
        return self._attribute["max_value"]

    def get_type(self):
        """ Returns the attribute effect type (positive, negative, or neutral) """
        return self._attribute["effect_type"]

    def get_value(self):
        """ Returns the attribute's value, use get_value_type to determine
        the type. """
        return self._attribute.get("value")

    def get_description(self):
        """ Returns the attribute's description string, if
        it is intended to be printed with the value there will
        be a "%s1" token somewhere in the string. Use
        get_description_formatted to substitute this automatically. """
        return self._attribute.get("description_string")

    def get_value_type(self):
        """ Returns the attribute's type. Currently this can be one of
        additive: An integer (convert value to integer) or boolean
        percentage: A standard percentage
        additive_percentage: Could represent a percentage that adds to default stats
        inverted_percentage: The sum of the difference between the value and 100%
        date: A unix timestamp """
        try: return self._attribute["description_format"][9:]
        except KeyError: return None

    def is_hidden(self):
        """ Returns True if the attribute is "hidden"
        (not intended to be shown to the end user). Note
        that hidden attributes also usually have no description string """
        if self._attribute.get("hidden", True) or self.get_description() == None:
            return True
        else:
            return False

    def __unicode__(self):
        """ Pretty printing """
        if not self.is_hidden():
            return self.get_description_formatted()
        else:
            return self.get_name() + ": " + self.get_value_formatted()

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __init__(self, attribute):
        self._attribute = attribute

        # Workaround until Valve gives sane values
        try:
            int(self.get_value())
            if (self.get_value_type() != "date" and
                self.get_value() > 1000000000 and
                "float_value" in self._attribute):
                self._attribute["value"] = self._attribute["float_value"]
        except TypeError:
            pass

class backpack:
    """ Functions for reading player inventory """

    def load(self, sid):
        """ Loads or refreshes the player backpack for the given steam.user
        Returns a list of items, will be empty if there's nothing in the backpack"""
        if not isinstance(sid, steam.user.profile):
            sid = steam.user.profile(sid)
        id64 = sid.get_id64()
        url = ("http://api.steampowered.com/ITFItems_440/GetPlayerItems/"
               "v0001/?key=" + steam.get_api_key() + "&format=json&SteamID=")
        inv = urllib2.urlopen(url + str(id64)).read()

        # Once again I'm doing what Valve should be doing before they generate
        # JSON. WORKAROUND
        self._inventory_object = json.loads(inv.replace("-1.#QNAN0", "0"))
        result = self._inventory_object["result"]["status"]
        if result == 8:
            raise TF2Error("Bad SteamID64 given")
        elif result == 15:
            raise TF2Error("Profile set to private")
        elif result != 1:
            raise TF2Error("Unknown error")

    def get_total_cells(self):
        """ Returns the total number of cells in the backpack.
        This can be used to determine if the user has bought a backpack
        expander. """
        return self._inventory_object["result"].get("num_backpack_slots", 0)

    def set_schema(self, schema):
        """ Sets a new item_schema to be used on inventory items """
        self._schema = schema

    def __iter__(self):
        return self.nextitem()

    def nextitem(self):
        iterindex = 0
        iterdata = self._inventory_object["result"]["items"]["item"]

        while(iterindex < len(iterdata)):
            data = item(self._schema, iterdata[iterindex])
            iterindex += 1
            yield data

    def __init__(self, sid = None, schema = None):
        """ Loads the backpack of user sid if given,
        generates a fresh schema object if one is not given. """

        self._schema = schema
        if not self._schema:
            self._schema = item_schema()
        if sid:
            self.load(sid)

class golden_wrench:
    """ Functions for reading info for the golden wrenches found
    during the Engineer update """

    _cache_basename = "tf2_golden_wrenches.js"

    def get_wrenches(self):
        """ Returns the list of wrenches """

        return self._wrench_list

    def get_wrench_for_user(self, user):
        """ If the user found a wrench a gw object will be returned
        Otherwise None """

        for w in self.get_wrenches():
            if w["steamID"] == user.get_id64():
                return w

    def get_craft_date(self, wrench):
        """ Returns the craft date as wrench as a time.struct_time object
        as returned from localtime """

        return time.localtime(wrench["timestamp"])

    def get_id(self, wrench):
        """ Returns the item ID (will match the ID in the user's inventory)
        This is NOT the unique number from the wrench log, see get_serial
        for that. """

        return wrench["itemID"]

    def get_serial(self, wrench):
        """ Returns the serial number of the wrench """

        return wrench["wrenchNumber"]

    def get_owner(self, wrench):
        """ Returns the 64 bit ID of the wrench owner """

        return wrench["steamID"]
    
    def __init__(self, fresh = False):
        """ Will rewrite the wrench file if fresh = True """

        self._wrench_url = ("http://api.steampowered.com/ITFItems_440/GetGoldenWrenches/"
                            "v0001/?key=" + steam.get_api_key() + "&format=json")

        cache = steam.get_cache_file(self._cache_basename)
        if fresh or not cache:
            cache = steam.write_cache_file(urllib2.urlopen(self._wrench_url),
                                           self._cache_basename)

        self._wrench_list = json.load(cache)["results"]["wrenches"]["wrench"]
