"""
Module for reading Portal 2 data using the Steam API

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

import items

class backpack(items.backpack):
    _app_id = "620"

    def __init__(self, sid = None, schema = None):
        if not schema: schema = item_schema()
        items.backpack.__init__(self, sid, schema)

class item_schema(items.schema):
    _app_id = "620"
    _class_map = items.MapDict([
            (1<<0, "P-body"),
            (1<<1, "Atlas")
            ])

    def create_item(self, oitem):
        return item(self, oitem)

    def __init__(self, lang = None):
        items.schema.__init__(self, lang)

class item(items.item):
    def get_full_item_name(self, prefixes = None):
        return items.item.get_full_item_name(self, None)

    def get_equipped_classes(self):
        """ The `equipped' field isn't exposed in Portal 2
        for one (probably silly) reason or another. So we still use the inventory
        token """
        inventory_token = self.get_inventory_token()
        classes = []

        for k,v in self._schema.get_classes().iteritems():
            if ((inventory_token & self.equipped_field) >> 16) & k:
                classes.append(v)

        return classes

    def __init__(self, schema, item):
        items.item.__init__(self, schema, item)
