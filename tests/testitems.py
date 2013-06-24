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

class InventoryBaseTestCase(unittest.TestCase):
    TEST_ID64 = 76561198014028523
    TEST_APPS = [440, 570, 620]

    @classmethod
    def setUpClass(cls):
        cls._inv = []

        for app in cls.TEST_APPS:
            cls._inv.append(items.inventory(app, cls.TEST_ID64))

class ItemTestCase(InventoryBaseTestCase):
    def test_position(self):
        for inv in self._inv:
            for item in inv:
                self.assertLessEqual(item.position, inv.cells_total)

    def test_equipped(self):
        for inv in self._inv:
            for item in inv:
                self.assertNotIn(0, item.equipped.keys())
                self.assertNotIn(65535, item.equipped.values())

    def test_name(self):
        pass

    def test_kill_eater(self):
        pass

class InventoryTestCase(InventoryBaseTestCase):
    def test_cell_count(self):
        for inv in self._inv:
            self.assertLessEqual(len(list(inv)), inv.cells_total)
