=======================
Steam Inventory Manager
=======================

High level item manager which scrapes data from http://steamcommunity.com instead
of Steam API.

.. autoclass:: steam.sim.inventory_context

    Fetches metadata of inventories for different games of given user:

        >>> inventory_context = steam.sim.inventory_context('76561198017493014')
        >>> inventory_context.apps
        [u'570', u'753', u'251970', u'440', u'620']
        >>> inventory_context.get(570)
        {u'name': u'Dota 2', u'trade_permissions': u'FULL', u'rgContexts': ...}

    This class also acts as an iterator of inventories:

        >>> for game_inventory_ctx in inventory_context:
        ...     game_inventory_ctx['name']
        ...
        u'Team Fortress 2'
        u'Dota 2'
        u'Portal 2'
        u'Steam'
        u'Sins of a Dark Age'

    Properties:

    .. autoattribute:: steam.sim.inventory_context.ctx

    .. autoattribute:: steam.sim.inventory_context.apps

    .. automethod:: steam.sim.inventory_context.get

.. autoclass:: steam.sim.inventory

    Takes :class:`steam.sim.inventory_context` and user id, and fetches data
    from given inventory:

        >>> inventory = steam.sim.inventory(inventory_context.get(570), '76561198017493014')
        >>> inventory.cells_total
        650

    This class also acts as an iterator yielding :class:`steam.sim.item` objects:

        >>> for item in inventory:
        ...     item.full_name
        ...
        u'Rattlebite'
        u'Heavenly Guardian Skirt'
        u'Gloried Horn of Druud'
        ...

    Properties:

    .. autoattribute:: steam.sim.inventory.cells_total

.. autoclass:: steam.sim.item

    Subclass of :class:`steam.items.item`. It is used as output from
    :class:`steam.sim.inventory`.

    On top of properties inherited from :class:`steam.items.item`, these are
    available:

    .. autoattribute:: steam.items.item.attributes

    .. autoattribute:: steam.sim.item.category

    .. autoattribute:: steam.sim.item.background_color

    .. autoattribute:: steam.sim.item.name

    .. autoattribute:: steam.sim.item.custom_name

    .. autoattribute:: steam.sim.item.name_color

    .. autoattribute:: steam.sim.item.full_name

    .. autoattribute:: steam.sim.item.hash_name

    .. autoattribute:: steam.sim.item.tool_metadata

    .. autoattribute:: steam.sim.item.tags

    .. autoattribute:: steam.sim.item.tradable

    .. autoattribute:: steam.sim.item.craftable

    .. autoattribute:: steam.sim.item.quality

    .. autoattribute:: steam.sim.item.quantity

    .. autoattribute:: steam.sim.item.attributes

    .. autoattribute:: steam.sim.item.position

    .. autoattribute:: steam.sim.item.schema_id

    .. autoattribute:: steam.sim.item.type

    .. autoattribute:: steam.sim.item.icon

    .. autoattribute:: steam.sim.item.image

    .. autoattribute:: steam.sim.item.id

    .. autoattribute:: steam.sim.item.slot_name

    .. autoattribute:: steam.sim.item.appid

.. autoclass:: steam.sim.item_attribute

    Subclass of :class:`steam.items.item_attribute`. It is used as output from
    :meth:`steam.sim.item.attributes`.

    On top of properties inherited from :meth:`steam.items.item_attribute`,
    these are available:

    .. autoattribute:: steam.sim.item_attribute.value_type

    .. autoattribute:: steam.sim.item_attribute.description

    .. autoattribute:: steam.sim.item_attribute.description_color

    .. autoattribute:: steam.sim.item_attribute.type

    .. autoattribute:: steam.sim.item_attribute.value
