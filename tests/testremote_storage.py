import unittest

try:
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import urlparse
    urlparse = urlparse.urlparse

from steam import remote_storage

class RemoteStorageTestCase(unittest.TestCase):
    APPID = 440
    INVALID_UGCID = "wobwobwobwob"

    VALID_UGCID = 650994986817657344
    VALID_UGC_SIZE = 134620
    VALID_UGC_FILENAME = "steamworkshop/tf2/_thumb.jpg"
    VALID_UGC_PATH = "/ugc/650994986817657344/D2ADAD7F19BFA9A99BD2B8850CC317DC6BA01BA9/" #Silly tea hat made by RJ

    @classmethod
    def setUpClass(cls):
        cls._test_file = remote_storage.ugc_file(cls.APPID, cls.VALID_UGCID)

    def test_invalid_ugcid(self):
        ugc_file = remote_storage.ugc_file(self.APPID, self.INVALID_UGCID)
        self.assertRaises(remote_storage.FileNotFoundError)

    def test_valid_ugcid_filename(self):
        self.assertEqual(self._test_file.filename, self.VALID_UGC_FILENAME)

    def test_valid_ugcid_size(self):
        self.assertEqual(self._test_file.size, self.VALID_UGC_SIZE)

    def test_valid_ugcid_url(self):
        parsed_url = urlparse(self._test_file.url)
        self.assertEqual(parsed_url.path, self.VALID_UGC_PATH)
