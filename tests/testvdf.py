import unittest
from steam import vdf

class SyntaxTestCase(unittest.TestCase):
    UNQUOTED_VDF = """
    node
    {
        key value
    }
    """

    QUOTED_VDF = """
    "node"
    {
        "key" "value"
    }
    """

    MACRO_UNQUOTED_VDF = """
    node
    {
        key value [$MACRO]
    }
    """

    MACRO_QUOTED_VDF = """
    "node"
    {
        "key" "value" [$MACRO]
    }
    """

    MIXED_VDF = """
    node
    {
        "key" value
        key2 "value"
        "key3" "value" [$MACRO]

        // Comment
        "subnode" [$MACRO]
        {
            key value
        }
    }
    """

    EXPECTED_DICT = {
            u"node": {
                u"key": u"value"
                }
            }

    EXPECTED_MIXED_DICT = {
            u"node": {
                u"key": u"value",
                u"key2": u"value",
                u"key3": u"value",
                u"subnode": {
                    u"key": u"value"
                    }
                }
            }

class DeserializeTestCase(SyntaxTestCase):
    def test_unquoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(self.UNQUOTED_VDF))

    def test_quoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(self.QUOTED_VDF))

    def test_macro_unquoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(self.MACRO_UNQUOTED_VDF))

    def test_macro_quoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(self.MACRO_QUOTED_VDF))

    def test_mixed(self):
        self.assertEqual(self.EXPECTED_MIXED_DICT, vdf.loads(self.MIXED_VDF))

class SerializeTestCase(SyntaxTestCase):
    def test_unquoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(vdf.dumps(vdf.loads(self.UNQUOTED_VDF))))

    def test_quoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(vdf.dumps(vdf.loads(self.QUOTED_VDF))))

    def test_macro_unquoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(vdf.dumps(vdf.loads(self.MACRO_UNQUOTED_VDF))))

    def test_macro_quoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(vdf.dumps(vdf.loads(self.MACRO_QUOTED_VDF))))

    def test_mixed(self):
        self.assertEqual(self.EXPECTED_MIXED_DICT, vdf.loads(vdf.dumps(vdf.loads(self.MIXED_VDF))))
