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

import base, time, os, urllib

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

class vanity_url(base.json_request):
    """ Class for holding a vanity URL and it's id64 """

    def get_id64(self):
        try:
            return self._id64
        except AttributeError:
            return None

    def __init__(self, vanity):
        """ Takes a vanity URL part and tries
        to resolve it. """

        url = ("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?" +
               urllib.urlencode({"key": base.get_api_key(), "vanityurl": vanity}))

        super(vanity_url, self).__init__(url)

        try:
            result = self._deserialize(self._download())["response"]
            scode = int(result["success"])
        except Exception as E:
            raise VanityError(E)

        if scode != 1:
            raise VanityError(result["message"], scode)

        self._id64 = long(result["steamid"])
        self._vanity = vanity

class profile(base.json_request):
    """ Functions for reading user account data """

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

    def __init__(self, sid):
        """ Creates a profile instance for the given user """
        url = ("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/"
               "v2/?key=" + base.get_api_key() + "&steamids=")

        sid = str(sid)
        lsid = sid.rfind('/')
        if (lsid + 1) >= len(sid): sid = sid[:lsid]
        sid = os.path.basename(sid)
        result = None

        super(profile, self).__init__(url + sid)

        if sid.isdigit():
            result = self._deserialize(self._download().decode("utf-8", errors="ignore"))["response"]["players"]

        if not result or not result[0]:
            try: sid = str(vanity_url(sid).get_id64())
            except VanityError as E:
                raise ProfileError("Profile id64 fetch for " + sid + " failed with: " + str(E))

            self._set_download_url(url + sid)
            result = self._deserialize(self._download())["response"]["players"]

        self._id64 = long(sid)
        self._summary_object = result[0]

    AVATAR_SMALL = "avatar"
    AVATAR_MEDIUM = "avatarmedium"
    AVATAR_LARGE = "avatarfull"
