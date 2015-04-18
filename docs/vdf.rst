===
VDF
===

|VDF|_ is format similar to JSON or YAML, used by Valve to store data. This
module mimics built-in :code:`json` module and provides functions for
serialization and deserialization of :code:`VDF` files.

.. autofunction:: steam.vdf.dump

.. code:: python

    >>> with open('dump.vdf', 'w') as file:
    ...     vdf.dump({u"key": u"value", u"list": [1, 2, 3]}, file)

    → cat dump.vdf
    "list"
    {
    "1" "1"
    "2" "1"
    "3" "1"
    }

    "key" "value"

.. autofunction:: steam.vdf.dumps

.. code:: python

    >>> vdf_obj = vdf.dumps({"key": "value", "list": [1, 2, 3]})
    >>> vdf_obj.decode('utf-16')
    u'\n  "list"\n  {\n    "1" "1"\n    "2" "1"\n    "3" "1"\n  }\n\n  "key" "value"\n'

.. autofunction:: steam.vdf.load

.. code:: python

    >>> with open('dump.vdf', 'r') as file:
    ...     vdf.load(file)
    ...
    {u'list': {u'1': u'1', u'3': u'1', u'2': u'1'}, u'key': u'value'}

.. autofunction:: steam.vdf.loads

.. code:: python

    >>> vdf.loads('"list" { "a" "1" "b" "2" "c" "3" }')
    {u'list': {u'a': u'1', u'c': u'3', u'b': u'2'}}

.. |VDF| replace:: :code:`VDF`
.. _VDF: https://wiki.teamfortress.com/wiki/WebAPI/VDF
