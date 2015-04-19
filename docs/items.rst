=====
Items
=====

.. autoclass:: steam.items.schema

    Fetching schema of Team Fortress 2 (id ``440``) would look like:

    .. code-block:: python

        >>> schema = steam.items.schema(440)
        >>> schema[340]
        <steam.items.item object at 0x10c871ed0>
        >>> schema[340].name
        u'Defiant Spartan'

    Schema class is an iterator of :meth:`steam.items.item` objects. There are
    also other meta properties available:

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

    .. code-block:: python

        >>> item = schema[340]
        >>> item.name
        u'Defiant Spartan'
        >>> item.type
        u'Hat'
        >>> item.attributes
        [<steam.items.item_attribute object at 0x10c8b3290>, <steam.items.item_attribute object at 0x10c8b3210>]

    As convenience, ``item`` acts also as iterator of its attributes:

    .. code-block:: python

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

    .. code-block:: python

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

    .. code-block:: python

        >>> import itertools
        >>> inventory = steam.items.inventory(570, 76561198017493014)
        >>> for item in itertools.islice(inventory, 2):
        ...     item.name
        ...
        '226749283'
        '226749284'

    Since inventory endpoint returns just very basic structure, we have to
    provide also ``schema`` if we want to work with fully populated :meth:`steam.items.item`
    objects:

    .. code-block:: python

        >>> schema = steam.items.schema(440)
        >>> inventory = steam.items.inventory(440, 76561198017493014, schema)
        >>> for item in itertools.islice(inventory, 2):
        ...     item.name
        ...
        u'Mercenary'
        u'Noise Maker - Winter Holiday'

    There also single meta property:

    .. autoattribute:: steam.items.inventory.cells_total

.. autoclass:: steam.items.assets

    Fetches store assets for ``app`` id. Assets class acts as an iterator of
    :meth:`steam.items.asset_item` objects.

    .. code-block:: python

        >>> import itertools
        >>> assets = steam.items.assets(440)
        >>> for asset in itertools.islice(assets, 2):
        ...     asset.price
        ...
        {u'MXN': 74.0, u'EUR': 4.59, u'VND': 109000.0, u'AUD': 6.5, ...}
        {u'MXN': 112.0, u'EUR': 6.99, u'VND': 159000.0, u'AUD': 9.8, ...}

    If you care only about single currency, ``currency`` keyword argument in
    `ISO 4217`_ format is also accepted.

    .. code-block:: python

        >>> assets = steam.items.assets(440, currency="RUB")
        >>> for asset in itertools.islice(assets, 2):
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
