import json, re, urllib2, urllib
from socket import timeout

__api_key = None

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
              "tr_TR": "Turkish"}

# Changeable if desired
_default_language = "en_US"

# Don't remember where this came from, or even if I wrote it. But thank
# you unnamed hero, or me. Not sure.
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
replace_exp = re.compile('[' + re.escape(control_chars) + ']')

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

class _interface_method(object):
    def __init__(self, iface, name):
        self._iface = iface
        self._name = name

    def __call__(self, method = "GET", version = 1, timeout = 5, since = None, **kwargs):
        kwargs["format"] = "json"
        kwargs["key"] = get_api_key()
        url = "http://api.steampowered.com/{0}/{1}/v{2}?{3}".format(self._iface,
                self._name, version, urllib.urlencode(kwargs))

        return method_result(url, last_modified = since, timeout = timeout)

class interface(object):
    def __init__(self, iface):
        self._iface = iface

    def __getattr__(self, name):
        return _interface_method(self._iface, name)

class http_downloader(object):
    def __init__(self, url, last_modified = None, timeout = 5):
        self._user_agent = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam Client/1366845241; ) AppleWebKit/535.15 (KHTML, like Gecko) Chrome/18.0.989.0 Safari/535.11"
        self._url = url
        self._timeout = timeout
        self._last_modified = last_modified

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
            req = urllib2.urlopen(urllib2.Request(self._url, headers = head), timeout = self._timeout)
            status_code = req.code
            body = req.read()
        except urllib2.HTTPError as E:
            raise HttpError("Server connection failed: {0.reason} ({1})".format(E, E.getcode()))
        except timeout:
            raise HttpTimeout("Server took too long to respond")

        lm = req.headers.get("last-modified")

        if status_code == 304:
            raise HttpStale(str(lm))
        elif status_code != 200:
            raise HttpError(str(status_code))
        else:
            self._last_modified = lm

        return body

    @property
    def last_modified(self):
        return self._last_modified

    @property
    def url(self):
        return self._url

class method_result(dict):
    """ Holds a deserialized JSON object obtained from fetching the given URL """
    def __init__(self, *args, **kwargs):
        super(method_result, self).__init__()
        self._fetched = False
        self._downloader = http_downloader(*args, **kwargs)

    def __getitem__(self, key):
        if not self._fetched:
            self._call_method()

        return super(method_result, self).__getitem__(key)

    def _call_method(self):
        """ Download the URL using last-modified timestamp if given """
        self.update(json.loads(self._strip_control_chars(self._downloader.download()).decode("utf-8", errors = "replace")))
        self._fetched = True

    def _strip_control_chars(self, s):
        return replace_exp.sub('', s)

    def get(self, key, default = None):
        if not self._fetched:
            self._call_method()

        return super(method_result, self).get(key, default)

def get_api_key():
    """ Returns the API key as a string, raises APIError if it's not set """

    if not __api_key:
        raise APIError("API key not set")

    return __api_key

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
    global __api_key

    __api_key = key

import apps, items, user, remote_storage, sim, vdf
