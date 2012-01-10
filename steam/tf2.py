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

import items, urllib2, json

class TF2Error(items.Error):
    def __init__(self, msg):
        items.Error.__init__(self)
        self.msg = msg

class item_schema(items.schema):
    _app_id = "440"
    _class_map = items.MapDict([
            (1, "Scout"),
            (3, "Soldier"),
            (7, "Pyro"),
            (4, "Demoman"),
            (6, "Heavy"),
            (9, "Engineer"),
            (5, "Medic"),
            (2, "Sniper"),
            (8, "Spy")
            ])

    def create_item(self, oitem):
        return item(self, oitem)

    def __init__(self, lang = None):
        items.schema.__init__(self, lang)

class backpack(items.backpack):
    _app_id = "440"

    def __init__(self, sid = None, schema = None):
        if not schema: schema = item_schema()
        items.backpack.__init__(self, sid, schema)

class item(items.item):
    def get_equipable_classes(self):
        classes = items.item.get_equipable_classes(self)

        if len(classes) <= 0 or classes[0] == None: return []
        else: return classes

    def __init__(self, schema, item):
        items.item.__init__(self, schema, item)

class assets(items.assets):
    _app_id = "440"

    def __init__(self, lang = None, currency = None):
        items.assets.__init__(self, lang, currency)

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
