import unittest
from steam import apps

class AppsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._apps = apps.app_list()

    def test_builtin_consistency(self):
        for app, name in self._apps._builtin.items():
            self.assertIn(app, self._apps)
            self.assertEquals((app, name), self._apps[app])

    def test_invalid_app(self):
        self.assertRaises(KeyError, self._apps.__getitem__, 12345678)
