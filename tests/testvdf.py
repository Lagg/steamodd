import unittest
from steam import vdf

class SyntaxTestCase(unittest.TestCase):
    # Deserialization
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

    COMMENT_QUOTED_VDF = """
    "node"
    {
        // Hi I'm a comment.
        "key" "value" [$MACRO]
    }
    """

    SUBNODE_QUOTED_VDF = """
    "node"
    {
        "subnode"
        {
            "key" "value"
        }
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

        "key4" "value"
    }
    """

    # Expectations
    EXPECTED_DICT = {
            u"node": {
                u"key": u"value"
                }
            }

    EXPECTED_SUBNODE_DICT = {
            u"node": {
                u"subnode": {
                    u"key": u"value"
                    }
                }
            }

    EXPECTED_MIXED_DICT = {
            u"node": {
                u"key": u"value",
                u"key2": u"value",
                u"key3": u"value",
                u"subnode": {
                    u"key": u"value"
                    },
                u"key4": u"value"
                }
            }

    # Serialization

    SIMPLE_DICT = EXPECTED_DICT
    SUBNODE_DICT = EXPECTED_SUBNODE_DICT

    ARRAY_DICT = {
            u"array": [
                u"a",
                u"b",
                u"c"]
            }

    NUMERICAL_DICT = {
            u"number": 1,
            u"number2": 2
            }

    COMBINATION_OF_ABOVE_DICT = {
            u"node": {
                u"key": u"value",
                u"subnode": {
                    u"key": u"value"
                    },
                u"array": [u"a", u"b", u"c", 1, 2, 3],
                u"number": 1024
                }
            }

    # Expectations
    EXPECTED_SIMPLE_DICT = SIMPLE_DICT
    EXPECTED_SUBNODE_DICT = SUBNODE_DICT

    EXPECTED_ARRAY_DICT = {
            "array": {
                "a": "1",
                "b": "1",
                "c": "1"
                }
            }

    EXPECTED_NUMERICAL_DICT = {
            "number": "1",
            "number2": "2"
            }

    EXPECTED_COMBINATION_OF_ABOVE_DICT = {
            "node": {
                "key": "value",
                "subnode": {
                    "key": "value"
                    },
                "array": {
                    "a": "1",
                    "b": "1",
                    "c": "1",
                    "1": "1",
                    "2": "1",
                    "3": "1"
                    },
                "number": "1024"
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

    def test_comment_quoted(self):
        self.assertEqual(self.EXPECTED_DICT, vdf.loads(self.COMMENT_QUOTED_VDF))

    def test_subnode_quoted(self):
        self.assertEqual(self.EXPECTED_SUBNODE_DICT, vdf.loads(self.SUBNODE_QUOTED_VDF))

    def test_mixed(self):
        self.assertEqual(self.EXPECTED_MIXED_DICT, vdf.loads(self.MIXED_VDF))


class SerializeTestCase(SyntaxTestCase):
    def test_simple_dict(self):
        self.assertEqual(self.EXPECTED_SIMPLE_DICT, vdf.loads(vdf.dumps(self.SIMPLE_DICT)))

    def test_subnode_dict(self):
        self.assertEqual(self.EXPECTED_SUBNODE_DICT, vdf.loads(vdf.dumps(self.SUBNODE_DICT)))

    def test_array_dict(self):
        self.assertEqual(self.EXPECTED_ARRAY_DICT, vdf.loads(vdf.dumps(self.ARRAY_DICT)))

    def test_numerical_dict(self):
        self.assertEqual(self.EXPECTED_NUMERICAL_DICT, vdf.loads(vdf.dumps(self.NUMERICAL_DICT)))

    def test_combination_of_above(self):
        self.assertEqual(self.EXPECTED_COMBINATION_OF_ABOVE_DICT, vdf.loads(vdf.dumps(self.COMBINATION_OF_ABOVE_DICT)))
