====
Apps
====

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
