"""
Steam profile/account reading and ID resolution
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

import time
import os
from . import api


class ProfileError(api.APIError):
    pass


class ProfileNotFoundError(ProfileError):
    pass


class VanityError(ProfileError):
    pass


class BansError(ProfileError):
    pass


class BansNotFoundError(BansError):
    pass


class vanity_url(object):
    """ Class for holding a vanity URL and its id64 """

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
                    raise VanityError(res.get("message",
                                              "Invalid vanity response"))
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
        self._api = api.interface("ISteamUser").ResolveVanityURL(vanityurl=vanity, **kwargs)


class profile(object):
    """ Functions for reading user account data """

    @property
    def id64(self):
        """ Returns the 64 bit steam ID (use with other API requests) """
        return int(self._prof["steamid"])

    @property
    def id32(self):
        """ Returns the 32 bit steam ID """
        return int(self.id64) - 76561197960265728

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
        5: looking to trade
        6: looking to play
        If player's profile is private, this will always be 0.
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

    @property
    def configured(self):
        """ Returns true if the user has created a Community profile """
        return bool(self._prof.get("profilestate"))

    @property
    def last_online(self):
        """ Returns the last time the user was online as a localtime
        time.struct_time struct """
        return time.localtime(self._prof["lastlogoff"])

    @property
    def comments_enabled(self):
        """ Returns true if the profile allows public comments """
        return bool(self._prof.get("commentpermission"))

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
        gameid = obj.get("gameid")
        gameserverip = obj.get("gameserverip")
        gameextrainfo = obj.get("gameextrainfo")
        return (int(gameid) if gameid else None, gameserverip, gameextrainfo)

    @property
    def location(self):
        """
        Returns a tuple of 2 elements (each of which may be None if not available):
        State ISO code, country ISO code
        """
        obj = self._prof
        return (obj.get("locstatecode"), obj.get("loccountrycode"))

    @property
    def lobbysteamid(self):
        """
        Returns a lobbynumber as int from few Source games or 0 if not in lobby.
        """
        return int(self._prof.get("lobbysteamid", 0))

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

    @property
    def level(self):
        """
        Returns the the user's profile level, note that this runs a separate
        request because the profile level data isn't in the standard player summary
        output even though it should be. Which is also why it's not implemented
        as a separate class. You won't need this output and not the profile output
        """

        level_key = "player_level"

        if level_key in self._api["response"]:
            return self._api["response"][level_key]

        try:
            lvl = api.interface("IPlayerService").GetSteamLevel(steamid=self.id64)["response"][level_key]
            self._api["response"][level_key] = lvl
            return lvl
        except:
            return -1

    @classmethod
    def from_def(cls, obj):
        """ Builds a profile object from a raw player summary object """
        prof = cls(obj["steamid"])
        prof._cache = obj

        return prof

    def __str__(self):
        return self.persona or str(self.id64)

    def __init__(self, sid, **kwargs):
        """ Creates a profile instance for the given user """
        try:
            sid = sid.id64
        except AttributeError:
            sid = os.path.basename(str(sid).strip('/'))

        self._cache = {}
        self._api = api.interface("ISteamUser").GetPlayerSummaries(version=2, steamids=sid, **kwargs)


class _batched_request(object):
    """ Base class for implementations that support multiple results
    per request (for example GetPlayerSummaries takes multiple id64s)
    """

    def __init__(self, batch, batchsize=100):
        self._batches = []
        batchlen, rem = divmod(len(batch), batchsize)

        if rem > 0:
            batchlen += 1

        for i in range(batchlen):
            offset = i * batchsize
            batch_chunk = batch[offset:offset + batchsize]

            self._batches.append(list(self._process_batch(batch_chunk)))

    def _process_batch(self, batch):
        """ Process the given batch and return
        an iterable
        """
        return batch

    def _call_method(self, batch):
        """ Call the desired method for the given batch and
        return the processed results as an iterable
        """
        raise NotImplementedError

    def __iter__(self):
        return next(self)

    def __next__(self):
        for batch in self._batches:
            for result in self._call_method(batch):
                yield result
    next = __next__


class profile_batch(_batched_request):
    def __init__(self, sids):
        """ Fetches user profiles en masse and generates 'profile' objects.
        The length of the ID list can be indefinite, separate requests
        will be made if the length exceeds the API's ID cap and the list
        split into batches. """
        super(profile_batch, self).__init__(sids)

    def _process_batch(self, batch):
        processed = set()

        for sid in batch:
            try:
                sid = sid.id64
            except AttributeError:
                sid = os.path.basename(str(sid).strip('/'))

            processed.add(str(sid))

        return processed

    def _call_method(self, batch):
        response = api.interface("ISteamUser").GetPlayerSummaries(version=2, steamids=','.join(batch))

        return [profile.from_def(player) for player in response["response"]["players"]]

class bans(object):
    def __init__(self, sid, **kwargs):
        """ Fetch user ban information """
        try:
            sid = sid.id64
        except AttributeError:
            sid = os.path.basename(str(sid).strip('/'))

        self._cache = {}
        self._api = api.interface("ISteamUser").GetPlayerBans(steamids=sid, **kwargs)

    @property
    def _bans(self):
        if not self._cache:
            try:
                res = self._api["players"]
                try:
                    self._cache = res[0]
                except IndexError:
                    raise BansNotFoundError("No ban results for this profile")
            except KeyError:
                raise BansError("Bad ban data returned")

        return self._cache

    @property
    def id64(self):
        return int(self._bans["SteamId"])

    @property
    def community(self):
        """ Community banned """
        return self._bans["CommunityBanned"]

    @property
    def vac(self):
        """ User is currently VAC banned """
        return self._bans["VACBanned"]

    @property
    def vac_count(self):
        """ Number of VAC bans on record """
        return self._bans["NumberOfVACBans"]

    @property
    def days_unbanned(self):
        """ Number of days since the last ban.
        Note that users without a ban on record will have
        this set to 0 so make sure to test bans.vac
        """
        return self._bans["DaysSinceLastBan"]

    @property
    def economy(self):
        """ Economy ban status which is a string for whatever reason """
        return self._bans["EconomyBan"]

    @property
    def game_count(self):
        """ Number of bans in games, this includes CS:GO Overwatch bans """
        return self._bans["NumberOfGameBans"]

    @classmethod
    def from_def(cls, obj):
        instance = cls(int(obj["SteamId"]))
        instance._cache = obj

        return instance


class bans_batch(_batched_request):
    def __init__(self, sids):
        super(bans_batch, self).__init__(sids)

    def _process_batch(self, batch):
        processed = set()

        for sid in batch:
            try:
                sid = sid.id64
            except AttributeError:
                sid = os.path.basename(str(sid).strip('/'))

            processed.add(str(sid))

        return processed

    def _call_method(self, batch):
        response = api.interface("ISteamUser").GetPlayerBans(steamids=','.join(batch))

        return [bans.from_def(player) for player in response["players"]]


class friend(object):
    """
    Class used to store friend obtained from GetFriendList.
    """
    def __init__(self, friend_dict):
        self._friend_dict = friend_dict

    @property
    def steamid(self):
        """ Returns the 64 bit Steam ID """
        return int(self._friend_dict["steamid"])

    @property
    def relationship(self):
        """ Returns relationship qualifier """
        return self._friend_dict["relationship"]

    @property
    def since(self):
        """ Returns date when relationship was created as a localtime time.struct_time """
        return time.localtime(self._friend_dict["friend_since"])


class friend_list(object):
    """
    Creates an iterator of friend objects fetched from given user's Steam ID.
    Allows for filtering by specyfing relationship argument in constructor,
    but API seems to always return items with friend relationship.
    Possible filter values: all, friend.
    """
    def __init__(self, sid, relationship="all", **kwargs):
        try:
            sid = sid.id64
        except AttributeError:
            sid = os.path.basename(str(sid).strip('/'))

        self._api = api.interface("ISteamUser").GetFriendList(steamid=sid,
                                                              relationship=relationship,
                                                              **kwargs)
        try:
            self._friends = self._api["friendslist"]["friends"]
        except api.HTTPFileNotFoundError:
            raise ProfileNotFoundError("Profile not found")
        except api.HTTPInternalServerError:
            raise ProfileNotFoundError("Invalid Steam ID given")

        self.index = 0

    @property
    def count(self):
        """ Returns number of friends """
        return len(self._friends)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self._friends):
            self.index += 1
            return friend(self._friends[self.index - 1])
        else:
            self.index = 0
            raise StopIteration

    next = __next__
