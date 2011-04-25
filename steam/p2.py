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
from collections import OrderedDict

class backpack(items.backpack):
    def __init__(self, sid = None, schema = None):
        self._app_id = "620"
        if not schema: schema = item_schema()
        items.backpack.__init__(self, sid, schema)

class item_schema(items.schema):
    def create_item(self, oitem):
        return item(self, oitem)

    def __init__(self, lang = None):
        self._app_id = "620"
        self.class_bits = OrderedDict([
                (1<<0, "P-body"),
                (1<<1, "Atlas")
                ])
        items.schema.__init__(self, lang)

class item(items.item):
    def get_equipable_classes(self):
        classes = items.item.get_equipable_classes(self)
        realclasses = []

        #Temporary WORKAROUND until the right class names are used
        for c in classes:
            if c == None: c = "Atlas"
            elif c == "eggbot": c = "P-body"

            realclasses.append(c)

        return realclasses

    def __init__(self, schema, item):
        items.item.__init__(self, schema, item)
