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

import items, json, base, time

_APP_ID = 440

class TF2Error(items.Error):
    def __init__(self, msg):
        items.Error.__init__(self, msg)
        self.msg = msg

class GoldenWrenchError(TF2Error):
    def __init__(self, msg):
        TF2Error.__init__(self, msg)
        self.msg = msg

class item_schema(items.schema):
    def __init__(self, appid = None, **kwargs):
        items.schema.__init__(self, appid or _APP_ID, item_type = item, **kwargs)

class backpack(items.backpack):
    def __init__(self, sid, appid = None, schema = None):
        items.backpack.__init__(self, appid or _APP_ID, sid, schema)

class item(items.item):
    def get_equipable_classes(self):
        classes = items.item.get_equipable_classes(self)

        if len(classes) <= 0 or classes[0] == None: return []
        else: return classes

    def __init__(self, schema, item):
        items.item.__init__(self, schema, item)

class assets(items.assets):
    def __init__(self, appid = None, **kwargs):
        items.assets.__init__(self, appid or _APP_ID, **kwargs)

class golden_wrench_item:
    def get_craft_date(self):
        """ Returns the craft date as wrench as a time.struct_time object
        as returned from localtime """

        return time.localtime(self._wrench["timestamp"])

    def get_id(self):
        """ Returns the item ID (will match the ID in the user's inventory)
        This is NOT the unique number from the wrench log, see get_serial
        for that. """

        return self._wrench["itemID"]

    def get_craft_number(self):
        """ Returns the number of the wrench in the order crafted """

        return self._wrench["wrenchNumber"]

    def get_owner(self):
        """ Returns the 64 bit ID of the wrench owner """

        return self._wrench["steamID"]

    def get_real_item(self):
        """ Returns the "real" item of the wrench
        this is an item compatible with steam.items.item classes
        and can be used as such. Note that this
        takes a while. Can be used to determine
        if wrench was deleted. """

        if not self._real_item:
            pack = backpack(self.get_owner())
            for item in pack:
                if item.get_id() == self.get_id():
                    self._real_item = item
                    return item

    def __init__(self, wrench):
        self._real_item = None
        self._wrench = wrench

class golden_wrench(base.json_request):
    """ Functions for reading info for the golden wrenches found
    during the Engineer update """

    def get_wrench_for_user(self, user):
        """ If the user found a wrench a gw object will be returned
        Otherwise None """

        for w in self:
            if w.get_owner() == user.get_id64():
                return w

    def __iter__(self):
        return self._nextitem()

    def _nextitem(self):
        obj = self._get()
        iterindex = 0
        data = sorted(set(obj.values()), key = golden_wrench_item.get_craft_number)

        while iterindex < len(data):
            ydata = data[iterindex]
            iterindex += 1
            yield ydata

    def __getitem__(self, key):
        return self._get(key)

    def _deserialize(self, data):
        res = super(golden_wrench, self)._deserialize(data)
        obj = {}

        try:
            wrenches = res["results"]["wrenches"]

            for wrench in wrenches:
                witem = golden_wrench_item(wrench)

                obj[witem.get_craft_number()] = witem
                obj[witem.get_id()] = witem
        except Exception as E:
            raise GoldenWrenchError("Failed to build wrench list: " + str(E))

        return obj

    def __init__(self):
        """ Fetch the ever-useful and ever-changing wrench owner list """
        url = ("http://api.steampowered.com/ITFItems_{0}/GetGoldenWrenches/"
               + "v2/?key={1}&format=json").format(_APP_ID, base.get_api_key())

        super(golden_wrench, self).__init__(url)
