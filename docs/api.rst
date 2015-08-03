==================
Steam API wrappers
==================


Low level methods
=================

You can call `any method from any of Steam API interfaces`_ using
:code:`steam.api.interface` class. Let's start with a quick example where we
fetch user's game library.

Start by importing :code:`interface` class:

    >>> from steam.api import interface


Call method :code:`GetOwnedGames` of interface :code:`IPlayerService`. We are
going to fetch games of user with id :code:`76561198017493014` and include all
application information:

    >>> games = interface('IPlayerService').GetOwnedGames(steamid=76561198017493014, include_appinfo=1)

Since all method calls are lazy by default, this doesn't do anything at all.
We'll need to either iterate over :code:`games`, :code:`print` it or access any
of its dictionary keys:

    >>> print(games['response']['game_count'])  # Fetches resource
    249

Don't worry, resource isn't fetched each time you access results.

    >>> print(games)  # Uses cached resource
    {'response': {'games': [{'name': 'Counter-Strike', 'playtime_forever': 1570,...

You can disable laziness of :code:`interface` by passing :code:`aggressive=True`
to its method:

    >>> games = interface('IPlayerService').GetOwnedGames(steamid=76561198017493014, include_appinfo=1, aggressive=True)

You can also pass :code:`since` (which translates to HTTP header :code:`If-Modified-Since`)
and :code:`timeout` to method. By default, :code:`version` is set to :code:`1`
and :code:`method` is :code:`GET`. Any number of additional keyword arguments is
supported, depending on given method (see `documentation`_).

.. _any method from any of Steam API interfaces:
    https://wiki.teamfortress.com/wiki/WebAPI#Methods

.. _documentation: https://wiki.teamfortress.com/wiki/WebAPI#Methods


High level methods
==================

Following classes are convenience wrappers around `Low level methods`_. :code:`kwargs`
are always passed to appropriate interface methods, so you can use all arguments
from previous section.


Apps
----

.. autoclass:: steam.apps.app_list

    >>> from steam.apps import app_list
    >>> app_list = app_list()
    >>> 'Dota 2' in app_list
    True
    >>> 'Half-Life 3' in app_list
    False
    >>> len(app_list)
    16762
    >>> app_list['Counter-Strike']
    (10, u'Counter-Strike')


Items
-----

.. autoclass:: steam.items.schema

    Fetching schema of Team Fortress 2 (id ``440``) would look like:

        >>> schema = steam.items.schema(440)
        >>> schema[340].name
        u'Defiant Spartan'

    Schema class is an iterator of :meth:`steam.items.item` objects. There are
    also other properties available:

    .. autoattribute:: steam.items.schema.client_url

    .. autoattribute:: steam.items.schema.language

    .. autoattribute:: steam.items.schema.attributes

    .. autoattribute:: steam.items.schema.origins

    .. autoattribute:: steam.items.schema.qualities

    .. autoattribute:: steam.items.schema.particle_systems

    .. autoattribute:: steam.items.schema.kill_ranks

    .. autoattribute:: steam.items.schema.kill_types


.. autoclass:: steam.items.item

    This is a simple wrapper around JSON representation of both schema and
    inventory items. It is composed mostly from item properties:

        >>> item = schema[340]
        >>> item.name
        u'Defiant Spartan'
        >>> item.type
        u'Hat'
        >>> item.attributes
        [<steam.items.item_attribute object at 0x10c8b3290>, <steam.items.item_attribute object at 0x10c8b3210>]

    As convenience, ``item`` acts also as iterator of its attributes:

        >>> for attribute in item.attributes:
        ...     attribute.name
        ...
        u'kill eater score type'
        u'kill eater kill type'

    Following properties are available:

    .. autoattribute:: steam.items.item.attributes

    .. autoattribute:: steam.items.item.quality

    .. autoattribute:: steam.items.item.inventory_token

    .. autoattribute:: steam.items.item.position

    .. autoattribute:: steam.items.item.equipped

    .. autoattribute:: steam.items.item.equipable_classes

    .. autoattribute:: steam.items.item.schema_id

    .. autoattribute:: steam.items.item.name

    .. autoattribute:: steam.items.item.type

    .. autoattribute:: steam.items.item.icon

    .. autoattribute:: steam.items.item.image

    .. autoattribute:: steam.items.item.id

    .. autoattribute:: steam.items.item.original_id

    .. autoattribute:: steam.items.item.level

    .. autoattribute:: steam.items.item.slot_name

    .. autoattribute:: steam.items.item.cvar_class

    .. autoattribute:: steam.items.item.craft_class

    .. autoattribute:: steam.items.item.craft_material_type

    .. autoattribute:: steam.items.item.custom_name

    .. autoattribute:: steam.items.item.custom_description

    .. autoattribute:: steam.items.item.quantity

    .. autoattribute:: steam.items.item.description

    .. autoattribute:: steam.items.item.min_level

    .. autoattribute:: steam.items.item.contents

    .. autoattribute:: steam.items.item.tradable

    .. autoattribute:: steam.items.item.craftable

    .. autoattribute:: steam.items.item.full_name

    .. autoattribute:: steam.items.item.kill_eaters

    .. autoattribute:: steam.items.item.rank

    .. autoattribute:: steam.items.item.available_styles

    .. autoattribute:: steam.items.item.style

    .. autoattribute:: steam.items.item.capabilities

    .. autoattribute:: steam.items.item.tool_metadata

    .. autoattribute:: steam.items.item.origin

.. autoclass:: steam.items.item_attribute

        >>> for attribute in item.attributes:
        ...     print('%s: %s' % (attribute.name, attribute.formatted_value))
        ...
        kill eater score type: 64.0
        kill eater kill type: 64.0

    Following properties are available:

    .. autoattribute:: steam.items.item_attribute.formatted_value

    .. autoattribute:: steam.items.item_attribute.formatted_description

    .. autoattribute:: steam.items.item_attribute.name

    .. autoattribute:: steam.items.item_attribute.cvar_class

    .. autoattribute:: steam.items.item_attribute.id

    .. autoattribute:: steam.items.item_attribute.type

    .. autoattribute:: steam.items.item_attribute.value

    .. autoattribute:: steam.items.item_attribute.value_int

    .. autoattribute:: steam.items.item_attribute.value_float

    .. autoattribute:: steam.items.item_attribute.description

    .. autoattribute:: steam.items.item_attribute.value_type

    .. autoattribute:: steam.items.item_attribute.hidden

    .. autoattribute:: steam.items.item_attribute.account_info

.. autoclass:: steam.items.inventory

    Fetches inventory of ``player`` for given ``app`` id:

        >>> inventory = steam.items.inventory(570, 76561198017493014)
        >>> for item in inventory:
        ...     item.name
        ...
        '226749283'
        '226749284'

    Since inventory endpoint returns just very basic structure, we have to
    provide also ``schema`` if we want to work with fully populated :meth:`steam.items.item`
    objects:

        >>> schema = steam.items.schema(440)
        >>> inventory = steam.items.inventory(440, 76561198017493014, schema)
        >>> for item in inventory:
        ...     item.name
        ...
        u'Mercenary'
        u'Noise Maker - Winter Holiday'

    There is also single property:

    .. autoattribute:: steam.items.inventory.cells_total

.. autoclass:: steam.items.assets

    Fetches store assets for ``app`` id. Assets class acts as an iterator of
    :meth:`steam.items.asset_item` objects.

        >>> assets = steam.items.assets(440)
        >>> for asset in assets:
        ...     asset.price
        ...
        {u'MXN': 74.0, u'EUR': 4.59, u'VND': 109000.0, u'AUD': 6.5, ...}
        {u'MXN': 112.0, u'EUR': 6.99, u'VND': 159000.0, u'AUD': 9.8, ...}

    If you care only about single currency, ``currency`` keyword argument in
    `ISO 4217`_ format is also accepted.

        >>> assets = steam.items.assets(440, currency="RUB")
        >>> for asset in assets:
        ...     asset.price
        ...
        {u'RUB': 290.0}
        {u'RUB': 435.0}

    All available tags of assets are available in following property:

    .. autoattribute:: steam.items.assets.tags

.. autoclass:: steam.items.asset_item

    .. autoattribute:: steam.items.asset_item.tags

    .. autoattribute:: steam.items.asset_item.base_price

    .. autoattribute:: steam.items.asset_item.price

    .. autoattribute:: steam.items.asset_item.name

.. _ISO 4217: http://en.wikipedia.org/wiki/ISO_4217


Localization
------------

.. autoclass:: steam.loc.language

    >>> language = steam.loc.language('nl_NL')
    >>> language.name
    'Dutch'
    >>> language.code
    'nl_NL'

    If language is not specified, it defaults to English:

    >>> language = steam.loc.language()
    >>> language.name
    'English'
    >>> language.code
    'en_US'

    If language isn't supported, ``__init__`` raises :meth:`steam.loc.LanguageUnsupportedError`

    >>> language = steam.loc.language('sk_SK')
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "steam/loc.py", line 68, in __init__
        raise LanguageUnsupportedError(code)
    steam.loc.LanguageUnsupportedError: sk_sk

    Properties:

    .. autoattribute:: steam.loc.language.code

    .. autoattribute:: steam.loc.language.name

.. autoclass:: steam.loc.LanguageUnsupportedError


Remote storage
--------------

Tools for probing Steam's UGC file storage system. UGC itself means User
Generated Content but in this context assume that such terms as "UGC ID" are
specific to Valve's system. UGC IDs are found in various places in the API and
Steam including decal attributes on TF2 items.

Practically speaking the purpose of `ugc_file` is similar to that of
:class:`steam.user.vanity_url`. Namely to convert an arbitrary ID into
something useful like a direct URL.

.. autoclass:: steam.remote_storage.ugc_file

    Fetches UGC file metadata for the given UGC and app ID.

        >>> ugc = steam.remote_storage.ugc_file(440, 650994986817657344)
        >>> ugc.url
        u'http://images.akamai.steamusercontent.com/ugc/650994986817657344/D2ADAD7F19BFA9A99BD2B8850CC317DC6BA01BA9/'

    Properties:

    .. autoattribute:: steam.remote_storage.ugc_file.size

    .. autoattribute:: steam.remote_storage.ugc_file.filename

    .. autoattribute:: steam.remote_storage.ugc_file.url

.. autoclass:: steam.remote_storage.FileNotFoundError


User
----

.. autoclass:: steam.user.vanity_url

    >>> vanity_url = steam.user.vanity_url('http://steamcommunity.com/id/ondrowan')
    >>> vanity_url.id64
    76561198017493014

.. autoclass:: steam.user.profile

    >>> profile = steam.user.profile('76561198017493014')
    >>> profile.persona
    u'Lich Buchannon'
    >>> profile.level
    37

    .. autoattribute:: steam.user.profile.id64

    .. autoattribute:: steam.user.profile.id32

    .. autoattribute:: steam.user.profile.persona

    .. autoattribute:: steam.user.profile.profile_url

    .. autoattribute:: steam.user.profile.vanity

    .. autoattribute:: steam.user.profile.avatar_small

    .. autoattribute:: steam.user.profile.avatar_medium

    .. autoattribute:: steam.user.profile.avatar_large

    .. autoattribute:: steam.user.profile.status

    .. autoattribute:: steam.user.profile.visibility

    .. autoattribute:: steam.user.profile.configured

    .. autoattribute:: steam.user.profile.last_online

    .. autoattribute:: steam.user.profile.comments_enabled

    .. autoattribute:: steam.user.profile.real_name

    .. autoattribute:: steam.user.profile.primary_group

    .. autoattribute:: steam.user.profile.creation_date

    .. autoattribute:: steam.user.profile.current_game

    .. autoattribute:: steam.user.profile.location

    .. autoattribute:: steam.user.profile.lobbysteamid

    .. autoattribute:: steam.user.profile.level

    .. automethod:: steam.user.profile.from_def

    .. autoattribute:: steam.user.profile.current_game

.. autoclass:: steam.user.profile_batch

    >>> profiles = steam.user.profile_batch(['76561198014028523', '76561198017493014'])
    >>> for profile in profiles:
    ...     profile.persona
    ...
    u'Lagg'
    u'Lich Buchannon'

.. autoclass:: steam.user.bans

    >>> bans = steam.user.bans('76561197962899758')
    >>> bans.vac
    True
    >>> bans.vac_count
    1
    >>> bans.days_unbanned
    2708

    .. autoattribute:: steam.user.bans.id64
    .. autoattribute:: steam.user.bans.community
    .. autoattribute:: steam.user.bans.vac
    .. autoattribute:: steam.user.bans.vac_count
    .. autoattribute:: steam.user.bans.days_unbanned
    .. autoattribute:: steam.user.bans.economy
    .. autoattribute:: steam.user.bans.game_count
    .. automethod:: steam.user.bans.from_def

.. autoclass:: steam.user.bans_batch

    >>> bans_batch = steam.user.bans_batch(['76561197962899758', '76561198017493014'])
    >>> for bans in bans_batch:
    ...     '%s: %s' % (bans.id64, bans.vac)
    ...
    '76561197962899758: True'
    '76561198017493014: False'
