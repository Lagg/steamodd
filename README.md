# About #

Steamodd originated with an early version of OPTF2 which itself
grew out of a 200 line script I wrote in the early days of the
Steam API to find things I could complain about. Since then it
has grown into a more and more capable and fully featured module
with every version.

It is still a work in progress and the API is subject to change
in breaking ways, however as of the 3.0 release I have began using
a simple and meaningful versioning system that should make moving
to new versions much easier. Major version numbers are incremented
when the release makes breaking changes, minor version numbers
are incremented when they are not. Meaning that it is safe to
upgrade without having to change existing code.

### The name ###

If there's one thing I've learned over the years and most recently
from OPTF2 it's a good idea to record the meaning behind your project
names if they aren't explicitly indicative of function or you *will*
forget.

Steamodd quite simply stands for "Steam odds and ends". Even though
it's starting to become more of a robust module it started out as a small
and probably not very well designed script meant to be run as a tool instead
of a reusable lib.

That's not to say that the name doesn't fit, since in
addition to the strong implementation of the API it has the recent
[VDF](http://wiki.teamfortress.com/wiki/WebAPI/VDF) support and the SIM
layer to boast as useful but not exactly unrelated utilities.

# Installing #

    $ pip install steamodd

If you wish to install it manually, Steamodd uses the standard distutils
module. To install it run `python setup.py install`. For further instructions
and commands run `python setup.py --help`.

# Using #

## Steam API key ##

Before calling any methods you should set Steam API key either from code:

```python
>>> import steam
>>> steam.api.key.set(API_KEY)
```

Or set environmental variable:

    $ export STEAMODD_API_KEY="your_key"

Most methods will not complete successfully without it. If you don't have an
API key you can register for one on [Steam](http://steamcommunity.com/dev/apikey).

## Low level API ##

You can call [any method from any of Steam API interfaces](https://wiki.teamfortress.com/wiki/WebAPI#Methods)
using `steam.api.interface` class. Let's start with a quick example where we
fetch user's game library.

Start by importing `interface` class:

```python
>>> from steam.api import interface
```

Call method `GetOwnedGames` of interface `IPlayerService`. We are going to
download games of user with id `76561198017493014` and include all application
information:

```python
>>> games = interface('IPlayerService').GetOwnedGames(steamid=76561198017493014, include_appinfo=1)
```

Since all method calls are lazy by default, this doesn't do anything at all.
We'll need to either iterate over `games`, `print` it or access any of its
dictionary keys:

```python
>>> print(games['response']['game_count'])  # Fetches resource
249
```

Don't worry, resource isn't fetched each time you access results.

```python
>>> print(games)  # Uses previously fetched resource
{'response': {'games': [{'name': 'Counter-Strike', 'playtime_forever': 1570,...
```

You can disable lazyness of `interface` by passing `aggressive=True` to its method:

```python
>>> games = interface('IPlayerService').GetOwnedGames(steamid=76561198017493014, include_appinfo=1, aggressive=True)
```

You can also pass `since` (which translates to HTTP header `If-Modified-Since`)
and `timeout` to method. By default, `version` is set to `1` and `method` is
`GET`. Any number of additional keyword arguments is supported, depending on
given method (see [documentation](https://wiki.teamfortress.com/wiki/WebAPI#Methods)).


# Testing #

To launch the test suite run `python setup.py run_tests -k <KEY>`.

[![Build Status](https://travis-ci.org/Lagg/steamodd.png)](https://travis-ci.org/Lagg/steamodd)

# Contributing #

If you would like to contribute please send a pull request.

# Bugs and feature requests #

Feel free to open an [issue](https://github.com/Lagg/steamodd/issues)
if you spot a bug or have an idea you would like to see go into steamodd.
