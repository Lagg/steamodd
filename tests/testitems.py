import unittest
from steam import items

class BaseTestCase(unittest.TestCase):
    TEST_APP = (440, 'en_US')     # TF2 English catalog
    ITEM_IN_CATALOG = 344         # Crocleather Slouch
    ITEM_NOT_IN_CATALOG = 1       # Demoman Bottle
    TEST_ID64 = 76561198014028523 # Yours truly

class AssetTestCase(BaseTestCase):
    def test_asset_contains(self):
        assets = items.assets(*self.TEST_APP)
        self.assertTrue(self.ITEM_IN_CATALOG in assets)
        self.assertFalse(self.ITEM_NOT_IN_CATALOG in assets)
        schema = items.schema(*self.TEST_APP)
        self.assertTrue(schema[self.ITEM_IN_CATALOG] in assets)
        self.assertFalse(schema[self.ITEM_NOT_IN_CATALOG] in assets)

class InventoryBaseTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls._schema = items.schema(*cls.TEST_APP)
        cls._inv = items.inventory(cls.TEST_APP[0], cls.TEST_ID64, cls._schema)

class ItemTestCase(InventoryBaseTestCase):
    def test_position(self):
        for item in self._inv:
            self.assertLessEqual(item.position, self._inv.cells_total)

    def test_equipped(self):
        for item in self._inv:
            self.assertNotIn(0, item.equipped.keys())
            self.assertNotIn(65535, item.equipped.values())

    def test_name(self):
        pass

    def test_kill_eater(self):
        pass

class InventoryTestCase(InventoryBaseTestCase):
    def test_cell_count(self):
        self.assertLessEqual(len(list(self._inv)), self._inv.cells_total)
