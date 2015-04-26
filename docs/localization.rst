============
Localization
============

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
