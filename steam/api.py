"""
Core API code
Copyright (c) 2010-2013, Anthony Garcia <anthony@lagg.me>
Distributed under the ISC License (see LICENSE)
"""

import os
import json
import socket
import sys

# Python 2 <-> 3 glue
try:
    from urllib.request import urlopen
    from urllib.request import Request as urlrequest
    from urllib.parse import urlencode
    from urllib import error as urlerror
except ImportError:
    from urllib2 import urlopen
    from urllib2 import Request as urlrequest
    from urllib import urlencode
    import urllib2 as urlerror


class SteamError(Exception):
    """ For future expansion, considering that steamodd is already no
    longer *just* an API implementation """
    pass


class APIError(SteamError):
    """ Base API exception class """
    pass


class APIKeyMissingError(APIError):
    pass


class HTTPError(APIError):
    """ Raised for other HTTP codes or results """
    pass


class HTTPStale(HTTPError):
    """ Raised for HTTP code 304 """
    pass


class HTTPTimeoutError(HTTPError):
    """ Raised for timeouts (not necessarily from the http lib itself but the
    socket layer, but the effect and recovery is the same, this just makes it
    more convenient """
    pass


class HTTPFileNotFoundError(HTTPError):
    """ Raised for HTTP code 404 """
    pass


class HTTPInternalServerError(HTTPError):
    """ Raised for HTTP code 500 """
    pass


class key(object):
    __api_key = None
    __api_key_env_var = os.environ.get("STEAMODD_API_KEY")

    @classmethod
    def set(cls, value):
        """ Set the current API key, overrides env var. """
        cls.__api_key = str(value)

    @classmethod
    def get(cls):
        """Get the current API key.
        if one has not been given via 'set' the env var STEAMODD_API_KEY will
        be checked instead.
        """
        apikey = cls.__api_key or cls.__api_key_env_var

        if apikey:
            return apikey
        else:
            raise APIKeyMissingError("API key not set")


class socket_timeout(object):
    """ Global timeout, can be overridden by timeouts passed to ctor """
    __timeout = 5

    @classmethod
    def set(cls, value):
        cls.__timeout = value

    @classmethod
    def get(cls):
        return cls.__timeout


class _interface_method(object):
    def __init__(self, iface, name):
        self._iface = iface
        self._name = name

    def __call__(self, version=1, timeout=None, since=None,
                 aggressive=False, data={}, **kwargs):
        kwargs.setdefault("format", "json")
        kwargs.setdefault("key", key.get())
        url = "http://api.steampowered.com/{0}/{1}/v{2}?{3}".format(self._iface,
                                                                    self._name,
                                                                    version,
                                                                    urlencode(kwargs))

        return method_result(url, last_modified=since, timeout=timeout, aggressive=aggressive, data=data)


class interface(object):
    def __init__(self, iface):
        self._iface = iface

    def __getattr__(self, name):
        return _interface_method(self._iface, name)


class http_downloader(object):
    def __init__(self, url, last_modified=None, timeout=None, data={}):
        self._user_agent = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam Client/1366845241; ) AppleWebKit/535.15 (KHTML, like Gecko) Chrome/18.0.989.0 Safari/535.11"
        self._url = url
        self._timeout = timeout or socket_timeout.get()
        self._last_modified = last_modified
        self._data = None

        if data:
            self._data = data

    def _build_headers(self):
        head = {}

        if self._last_modified:
            head["If-Modified-Since"] = str(self._last_modified)

        if self._user_agent:
            head["User-Agent"] = str(self._user_agent)

        return head

    def download(self):
        head = self._build_headers()
        status_code = -1
        body = ''

        try:
            if self._data:
                url_req = urlrequest(self._url, headers=head, data=urlencode(self._data))
            else:
                url_req = urlrequest(self._url, headers=head);

            req = urlopen(url_req, timeout=self._timeout)
            status_code = req.code
            body = req.read()
        except urlerror.HTTPError as E:
            code = E.getcode()
            # More portability hax (no reason property in 2.6?)
            try:
                reason = E.reason
            except AttributeError:
                reason = "Connection error"

            if code == 404:
                raise HTTPFileNotFoundError("File not found")
            elif code == 304:
                raise HTTPStale(str(self._last_modified))
            elif code == 500:
                raise HTTPInternalServerError("Internal Server Error")
            else:
                raise HTTPError("Server connection failed: {0} ({1})".format(reason, code))
        except (socket.timeout, urlerror.URLError):
            raise HTTPTimeoutError("Server took too long to respond")
        except socket.error as E:
            raise HTTPError("Server read error: {0}".format(E))

        lm = req.headers.get("last-modified")
        self._last_modified = lm

        return body

    @property
    def last_modified(self):
        return self._last_modified

    @property
    def url(self):
        return self._url


class method_result(dict):
    """ Holds a deserialized JSON object obtained from fetching the given URL.
    If aggressive is True then the data will be fetched when the method is called
    instead of only when the object is actually accessed.
    """

    def __handle_accessor(self, method, *args, **kwargs):
        try:
            if not self._fetched:
                self.call()
        except AttributeError:
            self._fetched = True

        return getattr(super(method_result, self), method)(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(method_result, self).__init__()
        self._fetched = False
        aggressive = kwargs.get("aggressive")

        if "aggressive" in kwargs:
            del kwargs["aggressive"]

        self._downloader = http_downloader(*args, **kwargs)

        if aggressive:
            self.call()

    def __getitem__(self, *args, **kwargs):
        return self.__handle_accessor("__getitem__", *args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.__handle_accessor("__setitem__", *args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.__handle_accessor("__delitem__", *args, **kwargs)

    def __iter__(self):
        return self.__handle_accessor("__iter__")

    def __contains__(self, *args, **kwargs):
        return self.__handle_accessor("__contains__", *args, **kwargs)

    def __len__(self):
        return self.__handle_accessor("__len__")

    def __str__(self):
        return self.__handle_accessor("__str__")

    def call(self):
        """ Make the API call again and fetch fresh data. """
        data = self._downloader.download()

        # Only try to pass errors arg if supported
        if sys.version >= "2.7":
            data = data.decode("utf-8", errors="ignore")
        else:
            data = data.decode("utf-8")

        self.update(json.loads(data))
        self._fetched = True

    def get(self, *args, **kwargs):
        return self.__handle_accessor("get", *args, **kwargs)

    def keys(self):
        return self.__handle_accessor("keys")
