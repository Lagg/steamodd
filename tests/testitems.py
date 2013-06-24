import unittest
from steam import items

class AssetTestCase(unittest.TestCase):
    TEST_APP = (440, 'en_US') # TF2 English catalog
    ITEM_IN_CATALOG = 344     # Crocleather Slouch
    ITEM_NOT_IN_CATALOG = 1   # Demoman Bottle

    def test_asset_contains(self):
        assets = items.assets(*self.TEST_APP)
        self.assertTrue(self.ITEM_IN_CATALOG in assets)
        self.assertFalse(self.ITEM_NOT_IN_CATALOG in assets)
        schema = items.schema(*self.TEST_APP)
        self.assertTrue(schema[self.ITEM_IN_CATALOG] in assets)
        self.assertFalse(schema[self.ITEM_NOT_IN_CATALOG] in assets)
