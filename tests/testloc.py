import unittest
import os
import steam


class LocTestCase(unittest.TestCase):
    DEFAULT_LANGUAGE_CODE = "en_US"
    VALID_LANGUAGE_CODE = "fi_FI"
    INVALID_LANGUAGE_CODE = "en_GB"

    def test_supported_language(self):
        lang = steam.loc.language(LocTestCase.VALID_LANGUAGE_CODE)
        self.assertEquals(lang._code, LocTestCase.VALID_LANGUAGE_CODE)

    def test_unsupported_language(self):
        self.assertRaises(steam.loc.LanguageUnsupportedError, steam.loc.language, LocTestCase.INVALID_LANGUAGE_CODE)

    def test_supported_language_via_environ(self):
        os.environ['LANG'] = LocTestCase.VALID_LANGUAGE_CODE
        lang = steam.loc.language(None)
        self.assertEquals(lang._code, LocTestCase.VALID_LANGUAGE_CODE)

    def test_unsupported_language_via_environ(self):
        os.environ['LANG'] = LocTestCase.INVALID_LANGUAGE_CODE
        lang = steam.loc.language(None)
        self.assertEquals(lang._code, LocTestCase.DEFAULT_LANGUAGE_CODE)


