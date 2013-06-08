import unittest
from steam import user

class ProfileTestCase(unittest.TestCase):
    VALID_ID64 = 76561198014028523
    INVALID_ID64 = 123
    # This is weird but there should be no reason that it's invalid
    # So Valve, if you see this, be gewd guys and make 33 bit (condensed)
    # IDs work properly. Or at least put a more appropriate error. Currently
    # It's impossible to distinguish between this and a bad ID (all are code 8)
    WEIRD_ID64 = (VALID_ID64 >> 33 << 33) ^ VALID_ID64

class VanityTestCase(unittest.TestCase):
    VALID_VANITY = "stragglerastic"
    INVALID_VANITY = "*F*SDF9"

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

    def test_weird_id(self):
        profile = user.profile(self.WEIRD_ID64)
        self.assertRaises(user.ProfileNotFoundError, lambda: profile.id64)
