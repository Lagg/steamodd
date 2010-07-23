#!/usr/bin/env python

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

import json, os, urllib2, time, steam, steam.user

_schema_url = ("http://api.steampowered.com/ITFItems_440/GetSchema/v0001/?key=" +
               steam.api_key + "&format=json&language=" + steam.language)

_inventory_url = ("http://api.steampowered.com/ITFItems_440/GetPlayerItems/"
                  "v0001/?key=" + steam.api_key + "&format=json&SteamID=")

_wrench_url = ("http://api.steampowered.com/ITFItems_440/GetGoldenWrenches/"
               "v0001/?key=" + steam.api_key + "&format=json")

# Random stuff that doesn't need to be downloaded every instance e.g. the schema
cache_dir = "tf2_pack"
if os.environ.has_key("XDG_CACHE_HOME"):
    cache_dir = os.path.join(os.environ["XDG_CACHE_HOME"], cache_dir)
elif os.environ.has_key("APPDATA"):
    cache_dir = os.path.join(os.environ["APPDATA"], cache_dir)

class TF2Error(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class backpack:
    """ Functions for reading player inventory """
    equipped_field = 0x1FF0000
    equipped_classes = {
        1<<8: "engineer",
        1<<7: "spy",
        1<<6: "pyro",
        1<<5: "heavy",
        1<<4: "medic",
        1<<3: "demoman",
        1<<2: "soldier",
        1<<1: "sniper",
        1<<0: "scout"
        }

    def _rewrite_schema_cache(self):
        """ Internal schema cache function, returns a stream """
        schema_handle = file(self._schema_file, "wb+")
        schema = urllib2.urlopen(_schema_url).read()
        schema_handle.write(schema)
        schema_handle.seek(0)

        return schema_handle
    
    def load_schema(self, fresh = False):
        """ Loads the item schema, if fresh is true a download is forced """
        schema_handle = 0
        self._schema_file = os.path.join(cache_dir, "schema.js")
        if fresh:
            try:
                schema_handle = self._rewrite_schema_cache()
            except URLError:
                raise TF2Error("Couldn't download schema")
        else:
            if os.path.exists(self._schema_file):
                schema_handle = file(self._schema_file, "rb")
            else:
                schema_handle = self._rewrite_schema_cache()

        self.schema_object = json.load(schema_handle)
        schema_handle.close()
        if self.schema_object["result"]["status"] != 1:
            raise TF2Error("Bad schema")
        return self.schema_object

    def load_pack(self, sid):
        """ Loads the player backpack for the given steam.user
        Returns a list of items, will be empty if there's nothing in the backpack"""
        id64 = sid.get_id64()

        self._inventory_object = json.load(urllib2.urlopen(_inventory_url + str(id64)))
        result = self._inventory_object["result"]["status"]
        if result == 8:
            raise TF2Error("Bad SteamID64 given")
        elif result == 15:
            raise TF2Error("Profile set to private")

        return self.get_items()

    def _internal_schema_get(self, item):
        for sitem in self.schema_object["result"]["items"]["item"]:
            if sitem["defindex"] == item["defindex"]:
                return sitem

    def get_item_schema(self, item):
        """ Looks up the schema block for the item, normally you want to use
        the functions that wrap this """

        schema = self._internal_schema_get(item)

        # We might need to update the cache
        if not schema:
            self.load_schema(fresh = True)

        schema = self._internal_schema_get(item)

        return schema

    def _internal_attr_get(self, compareby, obj):
        """ Internal function for special/schema attributes """
        attrs = []
        if obj.has_key("attributes"):
            for attr in obj["attributes"]["attribute"]:
                for sattr in self.schema_object["result"]["attributes"]["attribute"]:
                    if sattr[compareby] == attr[compareby]:
                        if sattr["description_string"] != "unused":
                            if sattr["attribute_class"] == "set_attached_particle":
                                sattr["description_string"] = "Particle Type: %s1"
                            sattr["value"] = attr["value"]
                            attrs.append(sattr)
                        break
        return attrs

    def get_item_attributes(self, item):
        """ Returns a list of attributes """
        return (self._internal_attr_get("name", self.get_item_schema(item)) +
                self._internal_attr_get("defindex", item))

    def get_item_quality(self, item):
        """ Returns a dict
        prettystr is the localized pretty name (e.g. Valve)
        id is the numerical quality (e.g. 8)
        str is the non-pretty string (e.g. developer) """
        quality = {}

        quality["id"] = item["quality"]

        for k,v in self.schema_object["result"]["qualities"].iteritems():
            if v == quality["id"]:
                quality["str"] = k
                break

        if self.schema_object["result"].has_key("qualityNames"):
            quality["prettystr"] = self.schema_object["result"]["qualityNames"][quality["str"]]
        else:
            quality["prettystr"] = quality["str"]

        return quality

    def get_item_position(self, item):
        """ Returns the item's position in the backpack or -1 if it's not
        in the backpack yet"""

        if item["inventory"] == 0:
            return -1
        else:
            return item["inventory"] & 0xFFFF

    def get_item_equipped_classes(self, item):
        """ Returns a list of classes (see equipped_classes values) """
        classes = []

        for k,v in self.equipped_classes.iteritems():
            if ((item["inventory"] & self.equipped_field) >> 16) & k:
                classes.append(v)

        return classes

    def get_items(self):
        """ Returns the list of backpack items """
        ilist = []
        if self._inventory_object:
            try:
                ilist = self._inventory_object["result"]["items"]["item"]
                if not ilist[0]:
                    ilist = []
            except KeyError:
                pass
        return ilist

    def format_attribute_description(self, attr):
        """ Returns a formatted description_string (%s* tokens replaced) """
        val = self.get_attribute_value(attr)
        ftype = self.get_attribute_value_type(attr)
        fattr = str(val)

        # I don't think %s2,%s3, etc. needs to be supported since there's
        # 1 value per attribute.
        if (ftype == "percentage" or ftype == "additive_percentage" or
            ftype == "inverted_percentage"):
            intp = int(val * 100)
            if intp >= 100:
                intp -= 100
            fattr = str(intp)
        elif ftype == "additive":
            if int(val) == val:
                fattr = (str(int(val)))
        elif ftype == "date":
            d = time.localtime(int(val))
            fattr = "%d-%02d-%02d" % (d.tm_year, d.tm_mon, d.tm_mday)

        return self.get_attribute_description(attr).replace("%s1", fattr)

    def get_item_name(self, item):
        """ Returns the item's name, this can be used with get_item_quality
        to decide prefixes (e.g. "The Kritzkrieg") for a unique item. """
        return self.get_item_schema(item)["item_name"]

    def get_item_type(self, item):
        """ Returns the item's type, e.g. "Kukri" for the Tribalman's Shiv """
        itype = self.get_item_schema(item)["item_type_name"]
        if itype == "TF_Wearable_Hat":
            itype = "Hat"
        return itype

    def get_attribute_type(self, attr):
        """ Returns the attribute effect type (positive, negative, or neutral) """
        return attr["effect_type"]

    def get_attribute_value(self, attr):
        """ Returns the attribute's value, use get_attribute_format to determine
        the type. """
        return attr["value"]

    def get_attribute_description(self, attr):
        """ Returns the attribute's UTF-8 encoded description string, if
        it is intended to be printed with the value there will
        be a "%s1" token somewhere in the string. Use
        format_attribute_description to substitute this automatically. """
        return attr["description_string"].encode("utf-8")

    def get_attribute_value_type(self, attr):
        """ Returns the attribute's type. Currently this can be one of
        additive: An integer (convert value to integer) or boolean
        percentage: A standard percentage
        additive_percentage: Could represent a percentage that adds to default stats
        inverted_percentage: The sum of the difference between the value and 100%
        date: A unix timestamp """
        return attr["description_format"][9:]

    def get_item_id(self, item):
        """ Returns the item's unique serial number """
        return item["id"]

    def get_item_level(self, item):
        """ Returns the item's level (e.g. 10 for The Axtinguisher) """
        return item["level"]

    def __init__(self, sid = None):
        """ Loads the backpack of user sid if given """
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.load_schema()

        if sid:
            self.load_pack(sid)

class golden_wrench:
    """ Functions for reading info for the golden wrenches found
    during the Engineer update """

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
    
    def __init__(self):
        self._wrench_list = (json.load(urllib2.urlopen(_wrench_url))
                             ["results"]["wrenches"]["wrench"])

