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
