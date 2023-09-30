import unittest
from steam import user
from steam import api

class ProfileTestCase(unittest.TestCase):
    VALID_ID64 = 76561198811195748
    VALID_ID32 = 850930020
    INVALID_ID64 = 123
    WEIRD_ID64 = (VALID_ID64 >> 33 << 33) ^ VALID_ID64

    VALID_VANITY = "spacecadet01"
    INVALID_VANITY = "*F*SDF9"

class VanityTestCase(ProfileTestCase):
    def test_invalid_vanity(self):
        vanity = user.vanity_url(self.INVALID_VANITY)
        self.assertRaises(user.VanityError, lambda: vanity.id64)

    def test_pathed_vanity(self):
        vanity = user.vanity_url('/' + self.VALID_VANITY + '/')
        self.assertEqual(vanity.id64, ProfileTestCase.VALID_ID64)

    def test_valid_vanity(self):
        vanity = user.vanity_url(self.VALID_VANITY)
        self.assertEqual(vanity.id64, ProfileTestCase.VALID_ID64)

class ProfileIdTestCase(ProfileTestCase):
    def test_invalid_id(self):
        profile = user.profile(self.INVALID_ID64)
        self.assertRaises(user.ProfileNotFoundError, lambda: profile.id64)

    def test_pathed_id(self):
        profile = user.profile('/' + str(self.VALID_ID64) + '/')
        self.assertEqual(profile.id64, self.VALID_ID64)

    def test_valid_id(self):
        profile = user.profile(self.VALID_ID64)
        self.assertEqual(profile.id64, self.VALID_ID64)
        self.assertEqual(profile.id32, self.VALID_ID32)

    def test_weird_id(self):
        profile = user.profile(self.WEIRD_ID64)
        self.assertRaises(user.ProfileNotFoundError, lambda: profile.id64)

class ProfileLevelTestCase(ProfileTestCase):
    def test_level(self):
        profile = user.profile(self.VALID_ID64)
        self.assertGreater(profile.level, 0)

class ProfileBatchTestCase(ProfileTestCase):
    def test_big_list(self):
        # Test id64 now lagg-bot test account, might need friends list adds
        # TODO: Implement GetFriendList in steamodd proper
        friends = api.interface("ISteamUser").GetFriendList(steamid = self.VALID_ID64)
        testsids = [friend["steamid"] for friend in friends["friendslist"]["friends"]]

        self.assertEqual(set(testsids), set(map(lambda x: str(x.id64), user.profile_batch(testsids))))
        self.assertEqual(set(testsids), set(map(lambda x: str(x.id64), user.bans_batch(testsids))))

    def test_compatibility(self):
        userlist = [self.VALID_ID64, user.vanity_url("windpower"), user.vanity_url("rjackson"),
                user.profile(self.VALID_ID64)]
        resolvedids = set()

        for u in userlist:
            try:
                sid = u.id64
            except AttributeError:
                sid = str(u)

            resolvedids.add(str(sid))

        self.assertEqual(resolvedids, set(map(lambda x: str(x.id64), user.profile_batch(userlist))))
        self.assertEqual(resolvedids, set(map(lambda x: str(x.id64), user.bans_batch(userlist))))

class FriendListTestCase(ProfileTestCase):
    def test_sids(self):
        profile_batch_friends = api.interface("ISteamUser").GetFriendList(steamid = self.VALID_ID64)
        profile_batch_testsids = [friend["steamid"] for friend in profile_batch_friends["friendslist"]["friends"]]
        friend_list = user.friend_list(self.VALID_ID64)

        self.assertEqual(set(profile_batch_testsids), set(map(lambda x: str(x.steamid), friend_list)))
