====
User
====

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
    .. automethod:: steam.user.bans.from_def

.. autoclass:: steam.user.bans_batch

    >>> bans_batch = steam.user.bans_batch(['76561197962899758', '76561198017493014'])
    >>> for bans in bans_batch:
    ...     '%s: %s' % (bans.id64, bans.vac)
    ...
    '76561197962899758: True'
    '76561198017493014: False'
