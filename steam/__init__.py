"""
A set of useful modules for reading data with the Steam API

Copyright (c) 2010, Anthony Garcia <lagg@lavabit.com>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import os, json
from user import *
from tf2 import *

__version__ = "0.8"

_api_key = None
_language = None

_cache_dir = "steamodd"
_config_dir = "steamodd.rc.d"
_core_config = "core.js"

class APIError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

def get_cache_dir():
    """ Returns the cache directory, you should use this if you're
    extending the modules """

    if not os.path.exists(_cache_dir):
        os.makedirs(_cache_dir)

    return _cache_dir

def get_config_dir():
    """ Returns the config directory """

    if not os.path.exists(_config_dir):
        os.makedirs(_config_dir)

    return _config_dir

def set_cache_dir(dirs):
    """ Set the cache directory. """
    global _cache_dir

    if not os.path.exists(dirs):
        os.makedirs(dirs)

    _cache_dir = dirs

def set_config_dir(dirs):
    """ Set the config file directory (your API key would be read from here) """
    global _config_dir

    if not os.path.exists(dirs):
        os.makedirs(dirs)

    _config_dir = dirs

def load_config_file(basename):
    """ Returns the configuration dict in basename
    from the config directory if available. """

    thefile = os.path.join(get_config_dir(), basename)
    if os.path.exists(thefile):
        try:
            fp = open(thefile, "rb")
            return json.load(fp)
        except:
            pass
    return {}

def write_config_file(config, basename):
    """ Writes the config dict to basename in the config dir. """

    confdir = get_config_dir()
    thefile = os.path.join(confdir, basename)

    if not os.path.exists(confdir):
        os.makedirs(confdir)

    try:
        fp = open(thefile, "wb+")
        json.dump(config, fp)
    except ValueError:
        pass

def get_cache_file(basename):
    """ Returns the cache file as a file object """
    thefile = os.path.join(get_cache_dir(), basename)
    if os.path.exists(thefile):
        try:
            return open(thefile, "rb")
        except IOError:
            raise Warning("Couldn't read cache file: " + thefile)

def write_cache_file(data, basename):
    """ Writes data to cache file basename. data should
    be a file-like object, returns a file object """

    cachedir = get_cache_dir()
    thefile = os.path.join(cachedir, basename)

    if not os.path.exists(cachedir):
        os.makedirs(cachedir)

    try:
        fp = open(thefile, "wb+")
        fp.write(data.read())
        fp.close()
        return get_cache_file(basename)
    except:
        try: os.unlink(thefile)
        except: pass
        raise Warning("Couldn't write cache file: " + thefile)

def get_api_key():
    """ Returns the API key as a string, raises APIError if it's not set """

    if not _api_key:
        raise APIError("API key not set")

    return _api_key

def set_api_key(key):
    global _api_key

    _api_key = key

def get_language():
    """ Returns the language code used for API requests """

    if not _language:
        raise APIError("Language not set")

    return _language

def set_language(lang):
    """ Should be a two char language code, e.g. 'en' for english """
    global _language

    _language = lang

if "XDG_CACHE_HOME" in os.environ:
    _cache_dir = os.path.join(os.environ["XDG_CACHE_HOME"], _cache_dir)
elif "APPDATA" in os.environ:
    _cache_dir = os.path.join(os.environ["APPDATA"], _cache_dir)

if "XDG_CONFIG_HOME" in os.environ:
    _config_dir = os.path.join(os.environ["XDG_CONFIG_HOME"], _config_dir)
elif "APPDATA" in os.environ:
    _config_dir = os.path.join(_cache_dir, _config_dir)

if os.path.exists(_config_dir):
    _config = load_config_file(_core_config)
else:
    _config = {}

if "api_key" in _config:
    _api_key = _config["api_key"]
if "language" in _config:
    _language = _config["language"]
