"""
Steam profile/account reading and ID resolution
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

import time, os
from . import api

class ProfileError(api.APIError):
    pass

class ProfileNotFoundError(ProfileError):
    pass

class VanityError(ProfileError):
    pass

class vanity_url(object):
    """ Class for holding a vanity URL and it's id64 """

    @property
    def id64(self):
        if self._cache:
            return self._cache

        res = None
        try:
            res = self._api["response"]
            self._cache = int(res["steamid"])
        except KeyError:
            if not self._cache:
                if res:
                    raise VanityError(res.get("message", "Invalid vanity response"))
                else:
                    raise VanityError("Empty vanity response")

        return self._cache

    def __str__(self):
        return str(self.id64)

    def __init__(self, vanity, **kwargs):
        """ Takes a vanity URL part and tries
        to resolve it. """
        vanity = os.path.basename(str(vanity).strip('/'))

        self._cache = None
        self._api = api.interface("ISteamUser").ResolveVanityURL(vanityurl = vanity, **kwargs)

class profile(object):
    """ Functions for reading user account data """

    @property
    def id64(self):
        """ Returns the 64 bit steam ID (use with other API requests) """
        return int(self._prof["steamid"])

    @property
    def persona(self):
        """ Returns the user's persona (what you usually see in-game) """
        return self._prof["personaname"]

    @property
    def profile_url(self):
        """ Returns a URL to the user's Community profile page """
        return self._prof["profileurl"]

    @property
    def vanity(self):
        """ Returns the user's vanity url if it exists, None otherwise """
        purl = self.profile_url.strip('/')
        if purl.find("/id/") != -1:
            return os.path.basename(purl)

    @property
    def avatar_small(self):
        return self._prof["avatar"]

    @property
    def avatar_medium(self):
        return self._prof["avatarmedium"]

    @property
    def avatar_large(self):
        return self._prof["avatarfull"]

    @property
    def status(self):
        """ Returns the user's status.
        0: offline
        1: online
        2: busy
        3: away
        4: snooze
        """
        return self._prof["personastate"]

    @property
    def visibility(self):
        """ Returns the visibility setting of the profile.
        1: private
        2: friends only
        3: public
        """
        return self._prof["communityvisibilitystate"]

    # This might be redundant, can we still get an id64 from an unconfigured profile?
    @property
    def configured(self):
        """ Returns true if the user has created a Community profile """
        return self._prof.get("profilestate", False)

    @property
    def last_online(self):
        """ Returns the last time the user was online as a localtime
        time.struct_time struct """
        return time.localtime(self._prof["lastlogoff"])

    @property
    def comments_enabled(self):
        """ Returns true if the profile allows public comments """
        return self._prof.get("commentpermission", False)

    @property
    def real_name(self):
        """ Returns the user's real name if it's set and public """
        return self._prof.get("realname")

    @property
    def primary_group(self):
        """ Returns the user's primary group ID if set. """
        return self._prof.get("primaryclanid")

    @property
    def creation_date(self):
        """ Returns the account creation date as a localtime time.struct_time
        struct if public"""
        timestamp = self._prof.get("timecreated")
        if timestamp:
            return time.localtime(timestamp)

    @property
    def current_game(self):
        """
        Returns a tuple of 3 elements (each of which may be None if not available):
        Current game app ID, server ip:port, misc. extra info (eg. game title)
        """
        obj = self._prof
        return (obj.get("gameid"), obj.get("gameserverip"), obj.get("gameextrainfo"))

    @property
    def location(self):
        """
        Returns a tuple of 2 elements (each of which may be None if not available):
        State ISO code, country ISO code
        """
        obj = self._prof
        return (obj.get("locstatecode"), obj.get("loccountrycode"))

    @property
    def _prof(self):
        if not self._cache:
            try:
                res = self._api["response"]["players"]
                try:
                    self._cache = res[0]
                except IndexError:
                    raise ProfileNotFoundError("Profile not found")
            except KeyError:
                raise ProfileError("Bad player profile results returned")

        return self._cache

    def __str__(self):
        return self.persona or str(self.id64)

    def __init__(self, sid, **kwargs):
        """ Creates a profile instance for the given user """
        try:
            sid = sid.id64
        except AttributeError:
            sid = os.path.basename(str(sid).strip('/'))

        self._cache = {}
        self._api = api.interface("ISteamUser").GetPlayerSummaries(version = 2, steamids = sid, **kwargs)
