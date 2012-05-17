from HTMLParser import HTMLParser
import re
import json
import base

class scriptParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._currentTag = None

    def handle_starttag(self, tag, attrs):
        self._currentTag = tag

    def handle_data(self, data):
        if self._currentTag == "script":
            ctx = re.match("var g_rgAppContextData = (.+);", data.strip())
            if ctx:
                self._ctxJSON = json.loads(ctx.groups()[0])

    def get_inventory_json(self):
        return self._ctxJSON

class backpack_context(base.json_request):
    """ Reads in inventory contexts and other information
    from the root inventory page """

    def get_app(self, key):
        """ Returns context data for a given app, can be an ID or a case insensitive name """

        keystr = str(key)
        res = None

        try:
            res = self._contexts[keystr]
        except KeyError:
            for k, v in self._contexts.iteritems():
                if "name" in v and v["name"].lower() == keystr.lower():
                    res = v
                    break

        if res: res["base_url"] = self._get_download_url()

        return res

    def get_app_list(self):
        """ Returns a list of valid app IDs """

        return self._contexts.keys()

    def _deserialize(self, data):
        parser = scriptParser()
        parser.feed(data)

        return parser.get_inventory_json()

    def __getitem__(self, key):
        res = self.get_app(key)

        if not res: raise KeyError(key)

        return res

    def __init__(self, user):

        if not isinstance(user, base.user.profile):
            self._profile = base.user.profile(user)
        else:
            self._profile = user

        url = "http://steamcommunity.com/profiles/{0}/inventory/".format(self._profile.get_id64())

        super(backpack_context, self).__init__(url)

        self._contexts = self._deserialize(self._download())

class backpack(base.json_request):
    def get_total_cells(self):
        """ Returns the total amount of "cells" which in this case is just an amount of items """
        return self._total_cells

    def nextitem(self):
        iterindex = 0
        iterdata = self._inventory_object

        while iterindex < len(iterdata):
            data = iterdata[iterindex]
            iterindex += 1
            yield data

    def __iter__(self):
        return self.nextitem()

    def __init__(self, app, schema = None, section = None):
        """ app: A valid app object as returned by backpack_context.get_app
        section: The inventory section to retrieve, if not given all items will be returned """

        self._inventory_object = []
        self._ctx = app
        user = None

        if isinstance(app, str):
            user = base.user.profile(app).get_id64()
        elif isinstance(app, base.user.profile):
            user = app.get_id64()

        # TODO first mode selection if user is passed
        if user: self._ctx = backpack_context(user)[104700]

        downloadlist = []
        url = "{0}json/{1}/".format(self._ctx["base_url"], self._ctx["appid"])
        contexts = self._ctx["rgContexts"]

        if section != None:
            sec = str(section)
            downloadlist.append(sec)
            self._total_cells = contexts[sec]["asset_count"]
        else:
            downloadlist = [str(k) for k in contexts.keys()]
            self._total_cells = self._ctx["asset_count"]

        for sec in downloadlist:
            super(backpack, self).__init__(url + sec)

            inventorysection = self._deserialize(self._download())

            itemdescs = inventorysection["rgDescriptions"]
            for k, v in inventorysection["rgInventory"].iteritems():
                fullitem = dict(v.items() + itemdescs[v["classid"] + "_" + v["instanceid"]].items())
                finalitem = item(fullitem)
                self._inventory_object.append(finalitem)

class item_attribute(base.items.item_attribute):
    def get_class(self):
        return "mult_burger"

    def get_id(self):
        # Make this be element position as well maybe
        return 0

    def get_name(self):
        return "make my name useful"

    def get_type(self):
        # Maybe map the tuples to a dict representing the 3 Valve ones if available TODO
        return self._attribute.get("color", "neutral")

    def get_description(self):
        # This should be fine for all uses since %s tokens aren't there
        desc = self._attribute.get("value")

        return desc or " "

    def is_hidden(self):
        # Never anything but this, but could have a use for child classes
        return False

    def get_value(self):
        return 0
    def get_value_formatted(self, value = None):
        return str(self.get_value())
    def get_value_max(self):
        return 0
    def get_value_min(self):
        return 0
    def get_value_type(self):
        return "value_is_additive"

    def __init__(self, attribute):
        super(item_attribute, self).__init__(attribute)

class item(base.items.item):
    def get_quality(self):
        nc = self._item["name_color"]

        for tag in self._get_category("Quality"):
            # Could maybe unpack hex values into ad-hoc ID.
            return {"id": 0, "prettystr": tag["name"], "str": tag["internal_name"]}

        return {"id": 0, "prettystr": nc, "str": nc}

    def get_name(self):
        return self._item["name"]

    def get_full_item_name(self, prefixes = {}):
        return self.get_name()

    def is_untradable(self):
        return bool(not self._item["tradable"])

    def get_quantity(self):
        return int(self._item["amount"])

    def get_attributes(self):
        # Use descriptions here, with alternative attribute class
        return [item_attribute(attr) for attr in self._item.get("descriptions", [])]

    def get_position(self):
        return self._item["pos"]

    def get_equipped_classes(self):
        # Unsupported
        return []

    def get_equipable_classes(self):
        # Needs supported tags
        classes = []
        
        for tag in self._get_category("Class"):
            classes.append(tag["name"])

        return classes

    def get_schema_id(self):
        # Kind of unsupported (class ID possible?) TODO
        return self._item["classid"]

    def get_type(self):
        return self._item.get("type", "")

    def get_image(self, size):
        smallicon = self._item["icon_url"]

        if not smallicon:
            return ""

        if size == self.ITEM_IMAGE_SMALL:
            return self._cdn_url + smallicon + "/96x96"
        elif size == self.ITEM_IMAGE_LARGE:
            return self._cdn_url + smallicon + "/512x512"

    def get_id(self):
        return long(self._item["id"])

    def get_level(self):
        # TODO (currently not in its own field, but included in type)
        return 0

    def get_slot(self):
        # (present sometimes in the form of tags) TODO
        for tag in self._get_category("Type"):
            return tag["name"]

    def get_description(self):
        # (kind of iffy here, since the actual descriptions are lists used for attributes)
        return None

    def is_name_prefixed(self):
        # Always false because of the nature of this inventory system, there's no accurate way to determine grammar
        return False

    def get_kill_eaters(self):
        # If they're there we can't tell due to lessened granularity, and Valve specific
        return []

    def get_rank(self):
        # see above
        return None

    def get_styles(self):
        # get_styles (Valve specific, and also iffy because it's 
        # technically there, but would need a heuristic because it's 
        # in the other description elements), the same is true for other related methods
        return []

    # get_capabilities (Maybe, depending on potential heuristic and tags) TODO

    def _get_category(self, name):
        cats = []

        if "tags" in self._item:
            for tag in self._item["tags"]:
                if tag["category"] == name:
                    cats.append(tag)

        return cats

    def __init__(self, theitem):
        self._cdn_url = "http://cdn.steamcommunity.com/economy/image/"

        super(item, self).__init__(None, theitem)

class item_schema(base.json_request):
    def __iter__(self):
        while False: yield None

    def get_classes(self):
        return {}

    def get_attributes(self):
        return []

    def get_particle_systems(self):
        return {}

    def __init__(self, lang = None, lm = None):
        self._app_id = 0
