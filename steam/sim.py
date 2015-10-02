"""
Steam Inventory Manager layer
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

from xml.sax import saxutils
import re
import json
import operator
from . import api
from . import items
from . import loc


class inventory_context(object):
    """ Builds context data that is fetched from a user's inventory page """

    @property
    def ctx(self):
        if self._cache:
            return self._cache

        try:
            data = self._downloader.download()
            contexts = re.search("var g_rgAppContextData = (.+);",
                                 data.decode("utf-8"))
            match = contexts.group(1)
            self._cache = json.loads(match)
        except:
            raise items.InventoryError("No SIM inventory information available for this user")

        return self._cache

    def get(self, key):
        """ Returns context data for a given app, can be an ID or a case insensitive name """
        keystr = str(key)
        res = None

        try:
            res = self.ctx[keystr]
        except KeyError:
            for k, v in self.ctx.items():
                if "name" in v and v["name"].lower() == keystr.lower():
                    res = v
                    break

        return res

    @property
    def apps(self):
        """ Returns a list of valid app IDs """
        return list(self.ctx.keys())

    def __getitem__(self, key):
        res = self.get(key)

        if not res:
            raise KeyError(key)

        return res

    def __iter__(self):
        return next(self)

    def __next__(self):
        iterindex = 0
        iterdata = sorted(self.ctx.values(), key=operator.itemgetter("appid"))

        while iterindex < len(iterdata):
            data = iterdata[iterindex]
            iterindex += 1
            yield data
    next = __next__

    def __init__(self, user, **kwargs):
        self._cache = {}
        try:
            sid = user.id64
        except:
            sid = user

        self._downloader = api.http_downloader("http://steamcommunity.com/profiles/{0}/inventory/".format(sid), **kwargs)
        self._user = sid


class inventory(object):
    @property
    def cells_total(self):
        """ Returns the total amount of "cells" which in this case is just an amount of items """
        return self._inv.get("cells", len(self))

    def __next__(self):
        iterindex = 0
        iterdata = self._inv.get("items", [])

        while iterindex < len(iterdata):
            data = iterdata[iterindex]
            iterindex += 1
            yield item(data, self._ctx["rgContexts"][data["sec"]])
    next = __next__

    def __getitem__(self, key):
        key = str(key)
        for item in self:
            if str(item.id) == key or str(item.original_id) == key:
                return item
        raise KeyError(key)

    def __iter__(self):
        return next(self)

    def __len__(self):
        return len(self._inv.get("items", []))

    @property
    def _inv(self):
        if self._cache:
            return self._cache

        downloadlist = []
        invstr = "http://steamcommunity.com/profiles/{0}/inventory/json/{1}/"
        url = invstr.format(self._user, self._ctx["appid"])
        contexts = self._ctx["rgContexts"]
        cellcount = 0
        merged_items = []

        if self._section is not None:
            sec = str(self._section)
            downloadlist = sec
            cellcount = contexts[sec]["asset_count"]
        else:
            for sec, ctx in contexts.items():
                cellcount += ctx["asset_count"]
                downloadlist.append(str(sec))

        for sec in downloadlist:
            page_url = url + sec

            if self._language:
                page_url += "?l=" + self._language

            req = api.http_downloader(page_url, timeout=self._timeout)
            inventorysection = json.loads(req.download().decode("utf-8"))

            if not inventorysection:
                raise items.InventoryError("Empty context data returned")

            try:
                itemdescs = inventorysection["rgDescriptions"]
            except KeyError:
                raise items.InventoryError("Steam returned inventory with missing context")

            inv = inventorysection.get("rgInventory")
            if not inv:
                continue

            for id, item in inv.items():
                # Store the section ID for later use
                item["sec"] = sec
                item.update(itemdescs.get(item["classid"] + "_" + item["instanceid"], {}))
                merged_items.append(item)

        self._cache = {"cells": cellcount, "items": merged_items}
        return self._cache

    def __init__(self, app, profile, schema=None, section=None, timeout=None, lang=None):
        """
        app is context data as returned by 'inventory_context.get'
        profile is a valid user object or ID64
        """

        self._cache = {}
        self._section = section
        self._ctx = app
        self._timeout = timeout or api.socket_timeout.get()
        self._language = loc.language(lang).name.lower()

        if not app:
            raise items.InventoryError("No inventory available")

        try:
            sid = profile.id64
        except AttributeError:
            sid = profile

        self._user = sid


class item_attribute(items.item_attribute):
    @property
    def value_type(self):
        # Because Valve uses this same data on web pages, it's /probably/
        # trustworthy, so long as they have fixed all the XSS bugs...
        return "html"

    @property
    def description(self):
        desc = self.value

        if desc:
            return saxutils.unescape(desc)
        else:
            return " "

    @property
    def description_color(self):
        """ Returns description color as an RGB tuple """
        return self._attribute.get("color")

    @property
    def type(self):
        return self._attribute.get("type")

    @property
    def value(self):
        return self._attribute.get("value")

    def __init__(self, attribute):
        super(item_attribute, self).__init__(attribute)


class item(items.item):
    @property
    def category(self):
        """ Returns the category name that the item is a member of """
        return self._ctx.get("name", self._ctx["id"])

    @property
    def background_color(self):
        """ Returns the color associated with the item as a hex RGB tuple """
        return self._item.get("background_color")

    @property
    def name(self):
        name = self._item.get("market_name")

        if not name:
            name = self._item["name"]

        return saxutils.unescape(name)

    @property
    def custom_name(self):
        name = saxutils.unescape(self._item["name"])

        if name.startswith("''"):
            return name.strip("''")

    @property
    def name_color(self):
        """ Returns the name color as an RGB tuple """
        return self._item.get("name_color")

    @property
    def full_name(self):
        return self.custom_name or self.name

    @property
    def hash_name(self):
        """ The URL-friendly identifier for the item. Generates its own approximation if one isn't available """
        name = self._item.get("market_hash_name")

        if not name:
            name = "{0.appid}-{0.name}".format(self)

        return name

    @property
    def tool_metadata(self):
        return self._item.get("app_data")

    @property
    def tags(self):
        """ A list of tags attached to the item if applicable, format is subject to change """
        return self._item.get("tags")

    @property
    def tradable(self):
        return self._item.get("tradable")

    @property
    def craftable(self):
        for attr in self:
            desc = attr.description
            if desc.startswith("( Not") and desc.find("Usable in Crafting"):
                return False

        return True

    @property
    def quality(self):
        """ Can't really trust presence of a schema here, but there is an ID sometimes """
        try:
            qid = int((self.tool_metadata or {}).get("quality", 0))
        except:
            qid = 0

        # We might be able to get the quality strings from the item's tags
        internal_name, name = "normal", "Normal"
        if self.tags:
            tags = {x.get('category'): x for x in self.tags}
            if 'Quality' in tags:
                internal_name, name = tags['Quality'].get('internal_name'), tags['Quality'].get('name')

        return qid, internal_name, name

    @property
    def quantity(self):
        return int(self._item["amount"])

    @property
    def attributes(self):
        # Use descriptions here, with alternative attribute class
        descs = self._item.get("descriptions") or []

        if descs:
            return [item_attribute(attr) for attr in descs]
        else:
            return []

    @property
    def position(self):
        return self._item["pos"]

    @property
    def schema_id(self):
        """
        This *will* return none if there is no schema ID, since it's a
        valve specific concept for the most part
        """
        try:
            return int((self.tool_metadata or {}).get("def_index"))
        except TypeError:
            return None

    @property
    def type(self):
        return self._item.get("type", '')

    def _scaled_image_url(self, dims):
        urlbase = self._item.get("icon_url")
        if urlbase:
            cdn = "http://cdn.steamcommunity.com/economy/image/"
            return cdn + urlbase + '/' + dims
        else:
            return ''

    @property
    def icon(self):
        return self._scaled_image_url("96fx96f")

    @property
    def image(self):
        return self._scaled_image_url("512fx512f")

    @property
    def id(self):
        return int(self._item["id"])

    @property
    def slot_name(self):
        # (present sometimes in the form of tags) TODO
        for tag in self._get_category("Type"):
            return tag["name"]

    @property
    def appid(self):
        """ Return the app ID that this item belongs to """
        return self._item["appid"]

    def _get_category(self, name):
        cats = []

        if self.tags:
            for tag in self.tags:
                if tag["category"] == name:
                    cats.append(tag)

        return cats

    def __init__(self, theitem, context):
        self._ctx = context

        super(item, self).__init__(theitem)
