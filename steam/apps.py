"""
Steam app metadata
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

from . import api


class AppError(api.APIError):
    pass


class app_list(object):
    """ Retrieves a list of all Steam apps with their ID and localized name. """
    _builtin = {
            753: "Steam",
            440: "Team Fortress 2",
            520: "Team Fortress 2 Beta",
            620: "Portal 2",
            570: "DOTA 2",
            205700: "DOTA 2 Test",
            816: "DOTA 2 Internal",
            730: "Counter Strike Global Offensive"
            }

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __getitem__(self, key):
        try:
            return key, self._builtin[key]
        except KeyError:
            key = str(key).lower()
            for app, name in self:
                if str(app) == key or name.lower() == key:
                    return app, name
            raise

    def __init__(self, **kwargs):
        self._api = api.interface("ISteamApps").GetAppList(version=2,
                                                           **kwargs)
        self._cache = {}

    def __iter__(self):
        return next(self)

    def __len__(self):
        return len(self._apps)

    @property
    def _apps(self):
        if not self._cache:
            try:
                self._cache = self._api["applist"]["apps"]
            except KeyError:
                raise AppError("Bad app list returned")
        return self._cache

    def __next__(self):
        i = 0
        data = self._apps

        while(i < len(data)):
            app = data[i]["appid"]
            name = data[i]["name"]
            i += 1
            yield (app, name)
    next = __next__
