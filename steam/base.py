import os, json, pycurl, re

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

class json_request(object):
    """ Base class for API requests over HTTP returning JSON """

    def _get_download_url(self):
        """ Returns the URL used for downloading the JSON data """
        return self._url

    def _set_download_url(self, url):
        self._url = url

    def _set_header(self, data):
        self._header += data

    def _set_body(self, data):
        self._body += data

    def _init_curl_single(self):
        """ Returns a new libcurl single/easy object """
        obj = pycurl.Curl()

        obj.setopt(pycurl.USERAGENT, self._user_agent)
        obj.setopt(pycurl.FOLLOWLOCATION, 1)
        obj.setopt(pycurl.NOSIGNAL, 1)
        obj.setopt(pycurl.CONNECTTIMEOUT, self._connect_timeout)
        obj.setopt(pycurl.TIMEOUT, self._timeout)

        return obj

    def _download(self, use_lm = False):
        """ Uses get_last_modified if use_lm is True """

        if self._body: return self._body

        curl_sync = self._init_curl_single()
        curl_sync.setopt(pycurl.URL, self._get_download_url())
        curl_sync.setopt(pycurl.WRITEFUNCTION, self._set_body)
        curl_sync.setopt(pycurl.HEADERFUNCTION, self._set_header)

        if use_lm:
            lm = self.get_last_modified()
            if lm: curl_sync.setopt(pycurl.HTTPHEADER, ["if-modified-since: " + lm])

        try:
            curl_sync.perform()
        except pycurl.error as E:
            raise HttpError(str(E))

        code = curl_sync.getinfo(pycurl.RESPONSE_CODE)

        header = self._header
        body = self._body

        curl_sync.close()

        if code == 304:
            raise HttpStale(str(self.get_last_modified()))
        elif code != 200:
            raise HttpError(str(code))
        else:
            hdict = self._make_header_dict(header)
            self._last_modified = hdict.get("last-modified")

            return body

    def _get(self, value = None):
        """ Internal JSON object getter """

        if not self._object:
            # Should use_lm always be here?
            self._object = self._deserialize(self._download(use_lm = True))

        if value:
            return self._object[value]
        else:
            return self._object

    def _deserialize(self, obj):
        try:
            return json.loads(obj)
        except ValueError:
            return json.loads(self._strip_control_chars(obj).decode("utf-8", errors = "replace"))

    def _strip_control_chars(self, s):
        return replace_exp.sub('', s)

    def _make_header_dict(self, value):
        hs = value.splitlines()
        hdict = {}

        for hdr in hs:
            sep = hdr.find(':')
            if sep != -1:
                hdict[hdr[:sep].strip().lower()] = hdr[sep + 1:].strip()

        return hdict

    def get_last_modified(self):
        """ Returns the last-modified header value """
        return self._last_modified

    def __init__(self, url, last_modified = None, timeout = 3, data_timeout = 15):
        self._last_modified = last_modified
        self._url = url
        self._user_agent = "Steamodd/2.0"
        self._connect_timeout = timeout
        self._timeout = data_timeout
        self._body = ""
        self._header = ""
        self._object = {}

class json_request_multi(object):
    """ Builds stacks of json_request-like objects and downloads them concurrently """

    def add(self, request):
        self._reqs.append(request)

    def download(self):
        reqs = self._reqs[:]
        finished = 0
        reqcount = len(reqs)
        conns = self._conns[:]
        newreqs = []

        while finished < reqcount:
            while reqs and conns:
                req = reqs.pop()
                conn = conns.pop()
                lm = req.get_last_modified()
                url = req._get_download_url()

                if lm:
                    conn.setopt(pycurl.HTTPHEADER, ["if-modified-since: " + lm])

                conn.setopt(pycurl.URL, url)
                conn.setopt(pycurl.WRITEFUNCTION, req._set_body)
                conn.setopt(pycurl.HEADERFUNCTION, req._set_header)
                conn.setopt(pycurl.USERAGENT, req._user_agent)
                conn.setopt(pycurl.CONNECTTIMEOUT, req._connect_timeout)
                conn.setopt(pycurl.TIMEOUT, req._timeout)

                conn.req = req

                self._multi.add_handle(conn)

            while True:
                res, handles = self._multi.perform()
                if res != pycurl.E_CALL_MULTI_PERFORM:
                    break

            while True:
                rem, done, err = self._multi.info_read()

                finished += len(done) + len(err)

                for handle in done:
                    req = handle.req
                    hdict = req._make_header_dict(req._header)
                    req._last_modified = hdict.get("last-modified")

                    newreqs.append(req)

                    self._multi.remove_handle(handle)
                    conns.append(handle)

                for handle, code, msg in err:
                    print code, msg
                    self._multi.remove_handle(handle)
                    conns.append(handle)

                if rem == 0:
                    break

            self._multi.select(1)

        return newreqs

    def close(self):
        for conn in self._conns:
            conn.close()
        self._multi.close()

    def __del__(self):
        self.close()

    def __init__(self, connsize = 10):
        self._conns = []
        self._multi = pycurl.CurlMulti()
        self._reqs = []

        for i in xrange(connsize):
            single = pycurl.Curl()

            single.setopt(pycurl.FOLLOWLOCATION, 1)
            single.setopt(pycurl.NOSIGNAL, 1)
            single.setopt(pycurl.TIMEOUT, 240)

            self._conns.append(single)

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
