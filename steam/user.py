"""
Module for reading Steam user account data

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

import json, urllib2, base, time, os, sqlite3, urllib

class ProfileError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return str(self.msg)

class VanityError(Exception):
    def __init__(self, msg, code = None):
        Exception.__init__(self)
        self.msg = msg
        self.code = code

    def __str__(self):
        return "{0}: {1}".format(self.get_code(), self.msg)

    def get_code(self):
        return self.code

class vanity_url:
    """ Class for holding a vanity URL and it's id64 """

    def get_id64(self):
        try:
            return self._id64
        except AttributeError:
            return None

    def __init__(self, vanity):
        """ Takes a vanity URL part and tries
        to resolve it. """

        self._url = ("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?" +
                     urllib.urlencode({"key": base.get_api_key(), "vanityurl": vanity}))

        try:
            result = json.load(urllib2.urlopen(self._url))["response"]
            scode = int(result["success"])
        except Exception as E:
            raise VanityError(E)

        if scode != 1:
            raise VanityError(result["message"], scode)

        self._id64 = long(result["steamid"])
        self._vanity = vanity

class profile:
    """ Functions for reading user account data """

    def _download(self):
        return urllib2.urlopen(self._get_download_url()).read()

    def _deserialize(self, data):
        return json.loads(data)

    def _get_download_url(self):
        return self._profile_url + str(self._id64)

    def get_summary(self, sid):
        """ Makes a best effort guess at fetching the profile
        for a given ID """

        sid = str(sid)
        if sid.isdigit():
            try:
                return self.get_summary_by_id64(sid)
            except ProfileError:
                pass
        return self.get_summary_by_vanity(sid)

    def get_summary_by_id64(self, sid):
        """ Attempts to fetch a profile assuming sid is a 64 bit ID """
        self._id64 = str(sid)
        try:
            self._summary_object = self._deserialize(self._download())["response"]["players"]["player"][0]
        except:
            raise ProfileError("Profile " + self._id64 + " (id64) not found")

        return self._summary_object

    def get_summary_by_vanity(self, sid):
        """ Attempts to fetch a profile assuming sid is a vanity URL part """

        sid = str(sid)
        lsid = sid.rfind('/')
        if (lsid + 1) >= len(sid): sid = sid[:lsid]
        sid = os.path.basename(sid)

        try: self._id64 = vanity_url(sid).get_id64()
        except VanityError as E:
            raise ProfileError("Profile id64 fetch for " + sid + " failed with: " + str(E))

        return self.get_summary_by_id64(self._id64)

    def get_id64(self):
        """ Returns the 64 bit steam ID (use with other API requests) """
        return self._summary_object["steamid"]

    def get_persona(self):
        """ Returns the user's persona (what you usually see in-game) """
        return self._summary_object["personaname"]

    def get_profile_url(self):
        """ Returns a URL to the user's Community profile page """
        return self._summary_object["profileurl"]

    def get_avatar_url(self, size):
        """ Returns a URL to the user's avatar, see AVATAR_* """
        return self._summary_object[size]

    def get_status(self):
        """ Returns the user's status.
        0: offline
        1: online
        2: busy
        3: away
        4: snooze
        """
        return self._summary_object["personastate"]

    def get_visibility(self):
        """ Returns the visibility setting of the profile.
        1: private
        2: friends only
        3: public
        """
        return self._summary_object["communityvisibilitystate"]

    # This might be redundant, can we still get an id64 from an unconfigured profile?
    def is_configured(self):
        """ Returns true if the user has created a Community profile """

        return self._summary_object.get("profilestate", False)

    def get_last_online(self):
        """ Returns the last time the user was online as a localtime
        time.struct_time struct """

        return time.localtime(self._summary_object["lastlogoff"])

    def is_comment_enabled(self):
        """ Returns true if the profile allows public comments """

        return self._summary_object.get("commentpermission", False)

    def get_real_name(self):
        """ Returns the user's real name if it's set and public """

        return self._summary_object.get("realname")

    # This isn't very useful yet since there's no API request
    # for groups yet, and I'm avoiding using the old API
    # as much as possible
    def get_primary_group(self):
        """ Returns the user's primary group ID if set. """

        return self._summary_object.get("primaryclanid")

    def get_creation_date(self):
        """ Returns the account creation date as a localtime time.struct_time
        struct if public"""

        timestamp = self._summary_object.get("timecreated")
        if timestamp:
            return time.localtime(timestamp)

    def get_current_game(self):
        """ Returns a dict of game info if the user is playing if public and set
        id is an integer if it's a steam game
        server is the IP address:port string if they're on a server
        extra is the game name """
        ret = {}
        if self.get_visibility() == 3:
            if "gameid" in self._summary_object:
                ret["id"] = self._summary_object["gameid"]
            if "gameserverip" in self._summary_object:
                ret["server"] = self._summary_object["gameserverip"]
            if "gameextrainfo" in self._summary_object:
                ret["extra"] = self._summary_object["gameextrainfo"]

            return ret

    def get_location(self):
        """ Returns a dict of location data if public and set
        country: A two char ISO country code
        state: A two char ISO state code """
        ret = {}
        if self.get_visibility() == 3:
            if "loccountrycode" in self._summary_object:
                ret["country"] = self._summary_object["loccountrycode"]
            if "locstatecode" in self._summary_object:
                ret["state"] = self._summary_object["locstatecode"]

            return ret

    def __init__(self, sid = None):
        """ Creates a profile instance for the given user """
        self._profile_url = ("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/"
                             "v0001/?key=" + base.get_api_key() + "&steamids=")

        if isinstance(sid, dict):
            self._summary_object = sid
        elif sid:
            self.get_summary(sid)

    AVATAR_SMALL = "avatar"
    AVATAR_MEDIUM = "avatarmedium"
    AVATAR_LARGE = "avatarfull"
