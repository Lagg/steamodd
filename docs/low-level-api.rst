=============
Low level API
=============

You can call `any method from any of Steam API interfaces`_ using
:code:`steam.api.interface` class. Let's start with a quick example where we
fetch user's game library.

Start by importing :code:`interface` class:

.. code-block:: python

    >>> from steam.api import interface


Call method :code:`GetOwnedGames` of interface :code:`IPlayerService`. We are
going to download games of user with id `76561198017493014` and include all
application information:

.. code-block:: python

    >>> games = interface('IPlayerService').GetOwnedGames(steamid=76561198017493014, include_appinfo=1)

Since all method calls are lazy by default, this doesn't do anything at all.
We'll need to either iterate over :code:`games`, :code:`print` it or access any
of its dictionary keys:

.. code-block:: python

    >>> print(games['response']['game_count'])  # Fetches resource
    249

Don't worry, resource isn't fetched each time you access results.

.. code-block:: python

    >>> print(games)  # Uses previously fetched resource
    {'response': {'games': [{'name': 'Counter-Strike', 'playtime_forever': 1570,...

You can disable lazyness of :code:`interface` by passing :code:`aggressive=True`
to its method:

.. code-block:: python

    >>> games = interface('IPlayerService').GetOwnedGames(steamid=76561198017493014, include_appinfo=1, aggressive=True)

You can also pass :code:`since` (which translates to HTTP header :code:`If-Modified-Since`)
and :code:`timeout` to method. By default, :code:`version` is set to :code:`1`
and :code:`method` is :code:`GET`. Any number of additional keyword arguments is
supported, depending on given method (see `documentation`_

.. _any method from any of Steam API interfaces:
    https://wiki.teamfortress.com/wiki/WebAPI#Methods

.. _documentation: https://wiki.teamfortress.com/wiki/WebAPI#Methods
