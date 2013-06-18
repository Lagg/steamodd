import unittest
from steam import apps

class AppsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._apps = apps.app_list()

    def test_app_list_get_tf2(self):
        self.assertEquals(self._apps[440], (440, 'Team Fortress 2'))

    def test_app_list_get_dota2(self):
        self.assertEquals(self._apps[570], (570, 'DOTA 2'))

    def test_app_list_get_invalid_app(self):
        self.assertRaises(apps.AppError, self._apps[12345678])
