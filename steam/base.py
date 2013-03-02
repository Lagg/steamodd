import json, re, urllib2
from socket import timeout

try:
    import requests
except ImportError:
    requests = None

try:
    import grequests
except ImportError:
    grequests = None

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

class http_request(object):
    def __init__(self, url, last_modified = None, timeout = 3, data_timeout = 15):
        self._user_agent = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam Client/1983; ) AppleWebKit/535.15 (KHTML, like Gecko) Chrome/18.0.989.0 Safari/535.11"
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

    def _deserialize(self, data):
        """ Deserialize downloaded content """

        return str(data)

    def _download(self):
        """ Download the URL using last-modified timestamp if given """

        using_requests = (requests and grequests)
        head = self._build_headers()
        status_code = -1
        body = ''

        if using_requests:
            req = requests.get(self._url, headers = head, timeout = self._timeout)
            status_code = req.status_code
            body = req.text
        else:
            try:
                req = urllib2.urlopen(urllib2.Request(self._url, headers = head), timeout = self._timeout)
            except timeout:
                raise HttpTimeout("Server took too long to respond")
            status_code = req.code
            body = req.read()

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

class json_request(http_request):
    """ Base class for API requests over HTTP returning JSON """

    def _get(self, value = None):
        """ Internal JSON object getter """

        if not self._object:
            self._object = self._deserialize(self._download())

        if value:
            return self._object[value]
        else:
            return self._object

    def _deserialize(self, data):
        try:
            return json.loads(data)
        except ValueError:
            try:
                return json.loads(self._strip_control_chars(data).decode("utf-8", errors = "replace"))
            except ValueError:
                return {}

    def _strip_control_chars(self, s):
        return replace_exp.sub('', s)

    def __init__(self, *args, **kwargs):
        self._object = {}

        super(json_request, self).__init__(*args, **kwargs)

class json_request_multi(object):
    """ Builds stacks of json_request-like objects and downloads them concurrently """

    def add(self, request):
        """ Adds the request to the list,
        remember that this is in place, object methods
        and properties will change """
        self._reqs[request.url] = request

    def clear_queue(self):
        self._reqs = {}

    def download(self):
        if requests and grequests:
            greqs = [grequests.get(request.url, headers = request._build_headers(), timeout = request._timeout) for request in self._reqs.values()]

            for response in grequests.map(greqs, size = self._connsize):
                req = None
                urlcandidates = [response.url] + [hist.url for hist in response.history]

                for url in urlcandidates:
                    try:
                        req = self._reqs[url]
                        break
                    except KeyError:
                        pass

                if req:
                    req._object = req._deserialize(response.text)
                    req._last_modified = response.headers.get("last-modified")
        else:
            for url in self._reqs.keys():
                req = self._reqs[url]
                req._get()

        return self._reqs.values()

    def __init__(self, connsize = None):
        self._reqs = {}
        self._connsize = connsize

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

import items, tf2, tf2b, p2, d2, d2b, user, remote_storage, sim, vdf
