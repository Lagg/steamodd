import unittest
from steam import apps

class AppsTestCase(unittest.TestCase):
    def test_app_list_get_tf2(self):
        self.assertEquals(apps.app_list()[440], (440, 'Team Fortress 2'))

    def test_app_list_get_dota2(self):
        self.assertEquals(apps.app_list()[570], (570, 'DOTA 2'))

    def test_app_list_get_invalid_app(self):
        self.assertRaises(apps.AppError, apps.app_list()[12345678])