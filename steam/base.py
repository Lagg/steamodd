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

    def _append_body(self, data):
        self._body += data

    def _append_header(self, data):
        self._header += data

    def _clear_buffers(self):
        self._body = ''
        self._header = ''

    def _get_download_url(self):
        """ Returns the URL used for downloading the JSON data """
        return self._url

    def _set_download_url(self, url):
        self._url = url

    def _init_curl_single(self):
        """ Returns a new libcurl single/easy object """
        obj = pycurl.Curl()

        obj.setopt(pycurl.USERAGENT, self._user_agent)
        obj.setopt(pycurl.FOLLOWLOCATION, 1)
        obj.setopt(pycurl.NOSIGNAL, 1)
        obj.setopt(pycurl.CONNECTTIMEOUT, self._connect_timeout)
        obj.setopt(pycurl.TIMEOUT, self._timeout)
        obj.setopt(pycurl.WRITEFUNCTION, self._append_body)
        obj.setopt(pycurl.HEADERFUNCTION, self._append_header)

        return obj

    def _download(self, use_lm = False):
        """ Uses get_last_modified if use_lm is True """

        if self._body: return self._body

        curl_sync = self._init_curl_single()
        curl_sync.setopt(pycurl.URL, self._get_download_url())

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
            try:
                return json.loads(self._strip_control_chars(obj).decode("utf-8", errors = "replace"))
            except ValueError:
                return {}

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
        self._user_agent = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam Client/1983; ) AppleWebKit/535.15 (KHTML, like Gecko) Chrome/18.0.989.0 Safari/535.11"
        self._connect_timeout = timeout
        self._timeout = data_timeout
        self._body = ""
        self._header = ""
        self._object = {}

class json_request_multi(object):
    """ Builds stacks of json_request-like objects and downloads them concurrently """

    def __del__(self):
        self._multi.close()

    def add(self, request):
        """ Adds the request to the list,
        remember that this is in place, object methods
        and properties will change """
        self._reqs.append(request)

    def clear_queue(self):
        self._reqs = []

    def download(self):
        finished = 0
        reqs = self._reqs[:]
        reqcount = len(reqs)

        cs = reqcount
        if self._connsize:
            cs = min(reqcount, self._connsize)

        self._multi.handles = []
        for i in xrange(cs):
            conn = pycurl.Curl()
            conn.setopt(pycurl.FOLLOWLOCATION, 1)
            conn.setopt(pycurl.NOSIGNAL, 1)
            self._multi.handles.append(conn)

        conns = self._multi.handles[:]

        while finished < reqcount:
            while reqs and conns:
                req = reqs.pop()
                lm = req.get_last_modified()
                url = req._get_download_url()

                req._clear_buffers()

                if lm:
                    conn.setopt(pycurl.HTTPHEADER, ["if-modified-since: " + lm])

                # TODO: req._init_curl_single
                conn = conns.pop()
                conn.setopt(pycurl.USERAGENT, req._user_agent)
                conn.setopt(pycurl.CONNECTTIMEOUT, req._connect_timeout)
                conn.setopt(pycurl.TIMEOUT, req._timeout)
                conn.setopt(pycurl.WRITEFUNCTION, req._append_body)
                conn.setopt(pycurl.HEADERFUNCTION, req._append_header)
                conn.setopt(pycurl.URL, url)

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

                    self._multi.remove_handle(handle)
                    conns.append(handle)

                for handle, code, msg in err:
                    print code, msg

                    self._multi.remove_handle(handle)
                    conns.append(handle)

                if rem == 0:
                    break

            self._multi.select(1)

        for conn in self._multi.handles:
            conn.close()

        return self._reqs

    def __init__(self, connsize = None):
        self._multi = pycurl.CurlMulti()
        self._reqs = []
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

import items, tf2, tf2b, p2, d2, d2b, user, remote_storage, sim
