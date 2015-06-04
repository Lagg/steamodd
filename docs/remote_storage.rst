==============
Remote storage
==============

Tools for probing Steam's UGC file storage system. UGC itself means User
Generated Content but in this context assume that such terms as "UGC ID" are
specific to Valve's system. UGC IDs are found in various places in the API and
Steam including decal attributes on TF2 items.

Practically speaking the purpose of ugc_file is similar to that of
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
