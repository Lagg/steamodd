import steam, sys, unittest, argparse

parser = argparse.ArgumentParser(description = "Steamodd test suite")
parser.add_argument("-k", "--key", help = "The API key to use in requests", required = True)
parser.add_argument("-l", "--language", help = "Language ISO code", default = "en_US")
parser.add_argument("-m", "--module", help = "Submodule to load classes from", default = "tf2")
args = parser.parse_args()

module = args.module
apikey = args.key
language = args.language

steam.set_api_key(apikey)

mod = getattr(steam, module)
schema = mod.item_schema(lang = language)

class TestSchema(unittest.TestCase):
    def test_item_lookup(self):
        iid = 0
        item = schema[iid]
        self.assertEquals(item.get_schema_id(), iid)
        with self.assertRaises(KeyError):
            schema[-1]

    def test_attr_name_map(self):
        mappedid = schema._get_attribute_id_for_value("DAMage PeNalty")

        self.assertEquals(mappedid, 1)
        self.assertIsNone(schema._get_attribute_id_for_value(1))

    def test_attr_lookup(self):
        attr = schema.get_attribute_definition("DAMage PENALTY")
        nattr = schema.get_attribute_definition(1)

        self.assertEquals(attr, nattr)

    def test_origin(self):
        self.assertTrue(schema.get_origin_name(3))
        self.assertIsNone(schema.get_origin_name("meh"))
        self.assertIsNone(schema.get_origin_name(None))
        self.assertIsNone(schema.get_origin_name(-324))

class TestSchemaItems(unittest.TestCase):
    def setUp(self):
        self._schema = schema

    def test_known_quality(self):
        for item in self._schema:
            quality = item.get_quality()
            self.assertTrue(quality)
            self.assertNotRegexpMatches(quality["str"], "^q\d+$")

    def test_equippable_by(self):
        for item in self._schema:
            classes = item.get_equipable_classes()
            self.assertItemsEqual(classes, filter(None, classes))

    def test_name(self):
        for item in self._schema:
            name = item.get_name()
            self.assertIsInstance(name, unicode)
            self.assertNotEqual(name, str(item.get_id()))

    def test_type(self):
        for item in self._schema:
            self.assertIsInstance(item.get_type(), unicode)

    def test_proper_name(self):
        for item in self._schema:
            name = item.get_full_item_name().encode("utf-8")
            quality = item.get_quality()
            rank = item.get_rank()
            q = quality["prettystr"]

            if rank: q = rank["name"]

            en_exp = "^{0}\s.+".format(q)
            other_exp = "^{0}\s+[(]{1}[)].*".format(item.get_name().encode("utf-8"), q)

            if not item.is_name_prefixed():
                if self._schema.get_language() == "en_US":
                    self.assertNotRegexpMatches(name, en_exp)
                else:
                    self.assertNotRegexpMatches(name, other_exp)
            else:
                if self._schema.get_language() == "en_US":
                    self.assertRegexpMatches(name, en_exp)
                else:
                    self.assertRegexpMatches(name, other_exp)

class TestSchemaItemAttributes(unittest.TestCase):
    def setUp(self):
        self._schema = schema

    def test_value_formatter(self):
        for item in self._schema:
            for attr in item:
                self.assertIsInstance(attr.get_value_formatted(), str)

    def test_description_formatter(self):
        for item in self._schema:
            for attr in item:
                desc = attr.get_description_formatted()
                rawval = attr.get_value_formatted()

                if not desc or attr.get_description().find("%s1") <= -1: continue

                self.assertRegexpMatches(desc, rawval)

    def test_value_types(self):
        for item in self._schema:
            for attr in item:
                self.assertIsInstance(attr.get_value_int(), int)
                self.assertIsInstance(attr.get_value_float(), float)

    def test_description_encoding(self):
        for item in self._schema:
            for attr in item:
                self.assertIsInstance(str(attr), str)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = (TestSchema, TestSchemaItems, TestSchemaItemAttributes)

    for test in tests:
        suite.addTest(loader.loadTestsFromTestCase(test))

    unittest.TextTestRunner(verbosity = 2).run(suite)
