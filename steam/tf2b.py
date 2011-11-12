"""
Module for reading Team Fortress 2 beta data using the Steam API

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

import tf2

class item_schema(tf2.item_schema):
    _app_id = "520"

    def _download(self):
        # WORKAROUND garbage characters
        return tf2.item_schema._download(self).replace("\xc4=", "Engineer")

    def __init__(self, lang = None):
        tf2.item_schema.__init__(self, lang)

class backpack(tf2.backpack):
    _app_id = "520"

    def __init__(self, sid = None, schema = None):
        tf2.backpack.__init__(self, sid, schema)
