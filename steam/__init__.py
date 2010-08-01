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

__version__ = "0.1"

api_key = None
language = None

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

    return _cache_dir

def get_config_dir():
    """ Returns the config directory """

    return _config_dir

def load_config_file(basename):
    """ Returns the configuration dict in basename
    from the config directory if available. """

    thefile = os.path.join(get_config_dir(), basename)
    if os.path.exists(thefile):
        try:
            fp = file(thefile, "rb")
            return json.load(fp)
        except:
            pass
    return {}

def write_config_file(config, basename):
    """ Writes the config dict to basename in the config dir. """

    thefile = os.path.join(get_config_dir(), basename)
    try:
        fp = file(thefile, "wb+")
        json.dump(config, fp)
    except ValueError:
        pass

def load_cache_file(basename):
    """ Returns the cache file content as a string or None
    if the file doesn't exist or can't be read """

    thefile = os.path.join(get_cache_dir(), basename)
    if os.path.exists(thefile):
        try:
            fp = file(thefile, "rb")
            return fp.read()
        except IOError:
            raise Warning("Couldn't read cache file: " + thefile)

def write_cache_file(data, basename):
    """ Writes data to cache file basename. data should
    be a file-like object """

    thefile = os.path.join(get_cache_dir(), basename)
    try:
        fp = file(thefile, "wb+")
        fp.write(data.read())
        fp.seek(0)
    except:
        try: os.unlink(thefile)
        except: pass
        raise Warning("Couldn't write cache file: " + thefile)

if os.environ.has_key("XDG_CACHE_HOME"):
    _cache_dir = os.path.join(os.environ["XDG_CACHE_HOME"], _cache_dir)
elif os.environ.has_key("APPDATA"):
    _cache_dir = os.path.join(os.environ["APPDATA"], _cache_dir)

if os.environ.has_key("XDG_CONFIG_HOME"):
    _config_dir = os.path.join(os.environ["XDG_CONFIG_HOME"], _config_dir)
elif os.environ.has_key("APPDATA"):
    _config_dir = os.path.join(_cache_dir, _config_dir)

if not os.path.exists(_cache_dir):
    os.makedirs(_cache_dir)
if not os.path.exists(_config_dir):
    os.makedirs(_config_dir)

_config = load_config_file(_core_config)

if _config.has_key("api_key"):
    api_key = _config["api_key"]
if _config.has_key("language"):
    language = _config["language"]
