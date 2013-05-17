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

## The name ##

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

# Using #

Before calling any methods you should call the steam.api.key.set
method and pass it your Steam API key. Most methods will not
complete successfully without it. If you don't have an API key you
can register for one on [Steam](http://steamcommunity.com/dev/apikey).

# Contributing #

If you would like to contribute please send a pull request.

# Bugs and feature requests #

Feel free to open an [issue](https://github.com/Lagg/steamodd/issues)
if you spot a bug or have an idea you would like to see go into steamodd.
