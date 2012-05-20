import os, json, urllib2, socket

_api_key = None

# Supported API languages (where applicable)
_languages = {"da_DK": "Danish",
              "nl_NL": "Dutch",
              "en_US": "English",
              "fi_FI": "Finnish",
              "fr_FR": "French",
              "de_DE": "German",
              "hu_HU": "Hungarian",
              "it_IT": "Italian",
              "ja_JP": "Japanese",
              "ko_KR": "Korean",
              "no_NO": "Norwegian",
              "pl_PL": "Polish",
              "pt_PT": "Portuguese",
              "pt_BR": "Brazilian Portuguese",
              "ro_RO": "Romanian",
              "ru_RU": "Russian",
              "zh_CN": "Simplified Chinese",
              "es_ES": "Spanish",
              "sv_SE": "Swedish",
              "zh_TW": "Traditional Chinese",
              "tr_TR": "Turksih"}

# Changeable if desired
_default_language = "en_US"

class APIError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

class HttpError(APIError):
    """ Raised for other HTTP codes or results """
    def __init__(self, msg):
        self.msg = msg
        APIError.__init__(self, msg)

class HttpStale(HttpError):
    """ Raised for HTTP code 304 """
    def __init__(self, msg):
        self.msg = msg
        HttpError.__init__(self, msg)

class HttpTimeout(HttpError):
    """ Raised for timeouts (may not explicitly be caused by HTTP lib) """
    def __init__(self, msg):
        self.msg = msg
        HttpError.__init__(self, msg)

class LangError(APIError):
    """ Base loc error class """
    def __init__(self, lang, msg = None):
        self.msg = lang + ": " + str(msg)
        APIError.__init__(self, self.msg)

class LangErrorUnsupported(LangError):
    """ Raised for invalid languages passed to related calls """
    def __init__(self, lang):
        LangError.__init__(self, lang, "Unsupported")

class json_request(object):
    """ Base class for API requests over HTTP returning JSON """

    def _get_download_url(self):
        """ Returns the URL used for downloading the JSON data """
        return self._url

    def _set_download_url(self, url):
        self._url = url

    def _download(self):
        """ Standard download, does no additional checks """
        req = urllib2.Request(self._get_download_url(), headers = {"User-Agent": self._user_agent})

        try: res = urllib2.urlopen(req)
        except urllib2.HTTPError as E: raise HttpError(str(E.getcode()))
        except socket.timeout: raise HttpTimeout("Socket level timeout")

        self._last_modified = res.headers.get("last-modified")
        return res.read()

    def _download_cached(self):
        """ Uses self.last_modified """
        req = urllib2.Request(self._get_download_url(), headers = {"If-Modified-Since": self.get_last_modified(),
                                                                   "User-Agent": self._user_agent})

        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            ecode = e.getcode()
            if ecode == 304:
                # No change
                raise HttpStale(str(self.get_last_modified()))
            else:
                raise HttpError(str(ecode))
        except socket.timeout:
            raise HttpTimeout("Socket level timeout")

        return res.read()

    def _deserialize(self, obj):
        return json.loads(obj)

    def get_last_modified(self):
        """ Returns the last-modified header value """
        return self._last_modified

    def __init__(self, url, last_modified = None):
        self._last_modified = last_modified
        self._url = url
        self._user_agent = "Steamodd/2.0"

def get_api_key():
    """ Returns the API key as a string, raises APIError if it's not set """

    if not _api_key:
        raise APIError("API key not set")

    return _api_key

def get_language(code = None):
    """ Returns tuple of (code, label) for a given language.
    raises LangErrorUnsupported if invalid, returns default if no code given """

    lang = None

    try:
        if not code:
            lang = (_default_language, _languages[_default_language])
        else:
            for k, v in _languages.iteritems():
                lk = k.lower()
                lc = code.lower()

                if (lk == lc or
                    lk.find('_') != -1 and lk.split('_')[0] == lc):
                    lang = (k, v)
    except KeyError:
        pass

    if not lang:
        raise LangErrorUnsupported(code)
    else:
        return lang

def set_api_key(key):
    global _api_key

    _api_key = key

import items, tf2, tf2b, p2, d2, d2b, user, remote_storage, sim
