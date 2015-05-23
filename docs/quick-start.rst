===========
Quick start
===========

Steam API key
-------------

If you are going to use Steam API, you'll need to set Steam API key either from
code:

    >>> import steam
    >>> steam.api.key.set(API_KEY)

Or set environmental variable:

.. code-block:: bash

    $ export STEAMODD_API_KEY="your_key"

Most methods will not complete successfully without it. If you don't have an
API key you can register for one on `Steam`_.

.. _Steam: http://steamcommunity.com/dev/apikey


Components
----------

This library consists of three major components, which are documented separately:

* :doc:`api`
* :doc:`sim`
* :doc:`vdf`
