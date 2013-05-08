"""
Module for reading from the remote storage service

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

import json, base

class UGCError(base.APIError):
    def __init__(self, msg):
        self.msg = msg
        base.APIError.__init__(self, msg)

class ugc_file(object):
    @property
    def size(self):
        """ Size in bytes """
        return self._data["size"]

    @property
    def filename(self):
        """ Local filename is what the user named it, not the URL """
        return self._data["filename"]

    @property
    def url(self):
        """ UGC link """
        return self._data["url"]

    @property
    def _data(self):
        if self._cache:
            return self._cache

        data = None
        status = None
        try:
            data = self._api["data"]
            status = self._api["status"]["code"]
        except KeyError:
            if not data:
                if status != None and status != 9:
                    raise UGCError("Code " + str(status))
                else:
                    raise UGCError("File not found")

        self._cache = data
        return self._cache

    def __init__(self, appid, ugcid64, **kwargs):
        self._cache = {}
        self._api = base.interface("ISteamRemoteStorage").GetUGCFileDetails(ugcid = ugcid64, appid = appid, **kwargs)
