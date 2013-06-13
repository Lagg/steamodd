import unittest
from steam import remote_storage

class RemoteStorageTestCase(unittest.TestCase):
    APPID = 440
    INVALID_UGCID = "wobwobwobwob"

    VALID_UGCID = 650994986817657344
    VALID_UGC_SIZE = 134620
    VALID_UGC_FILENAME = "steamworkshop/tf2/_thumb.jpg"
    VALID_UGC_URL = "http://cloud-2.steampowered.com/ugc/650994986817657344/D2ADAD7F19BFA9A99BD2B8850CC317DC6BA01BA9/"


    def test_invalid_ugcid(self):
        ugc_file = remote_storage.ugc_file(self.APPID, self.INVALID_UGCID)
        self.assertRaises(remote_storage.FileNotFoundError)

    def test_valid_ugcid_filename(self):
        ugc_file = remote_storage.ugc_file(self.APPID, self.VALID_UGCID)
        self.assertEqual(ugc_file.filename, self.VALID_UGC_FILENAME)

    def test_valid_ugcid_size(self):
        ugc_file = remote_storage.ugc_file(self.APPID, self.VALID_UGCID)
        self.assertEqual(ugc_file.size, self.VALID_UGC_SIZE)

    def test_valid_ugcid_url(self):
        ugc_file = remote_storage.ugc_file(self.APPID, self.VALID_UGCID)
        self.assertEqual(ugc_file.url, self.VALID_UGC_URL)