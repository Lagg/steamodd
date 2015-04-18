===========
Quick start
===========

Steam API key
-------------

Before calling any methods you should set Steam API key either from code:

.. code-block:: python

    >>> import steam
    >>> steam.api.key.set(API_KEY)

Or set environmental variable:

.. code-block:: bash

    $ export STEAMODD_API_KEY="your_key"

Most methods will not complete successfully without it. If you don't have an
API key you can register for one on `Steam`_.

.. _Steam: http://steamcommunity.com/dev/apikey


Using Steam API wrappers
------------------------

Majority of this library constists of wrappers around Steam API endpoints. So,
let's call some:

.. code-block:: python

    >>> app_list = steam.apps.app_list()
    >>> 'Dota 2' in app_list
    True
    >>> 'Half-Life 3' in app_list
    False
    >>> len(app_list)
    16762
    >>> app_list['Counter-Strike']
    (10, u'Counter-Strike')

That's mostly what these wrappers do. Every endpoint is different and each of
them is documented separately.
