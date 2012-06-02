"""
VDF (de)serialization

Copyright (c) 2010-2012, Anthony Garcia <lagg@lavabit.com>

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

from collections import deque
import re
import cStringIO

def NODE_STRING(match):
    return cast_to_num(match)

def NODE_OPENER(match):
    pass

def NODE_CLOSER(match):
    pass

def NODE_COMMENT(match):
    comment = match.strip()
    return comment

def NEWLINE(match):
    pass

# This isn't a dict because order is important.
# Backwards token stack = not gewd
grammar = [
    ('"([^"]*)"', NODE_STRING),
    ('{', NODE_OPENER),
    ('}', NODE_CLOSER),
    ('//(.*)$', NODE_COMMENT),
    ('\Z', NEWLINE)
]

def scan(stream):
    stack = []

    line = stream.readline()
    while line:
        for tok in grammar:
            match = re.findall(tok[0], line, flags = re.UNICODE)
            for m in match:
                func = tok[1]
                token = []

                token.append(func.__name__)
                value = func(m)
                if value != None:
                    token.append(value)
                stack.append(token)
        line = stream.readline()

    return deque(stack)

def cast_to_num(string):
    num = re.match("^\s*(-?\d+\.?\d*)\s*$", string, flags = re.UNICODE)
    if num:
        catch = num.groups()[0]
        if catch.find('.') != -1: return float(catch)
        else: return int(catch)
    else:
        return string

def read_node(stack):
    deserialized = {}
    lastpop = None
    laststring = None

    while stack:
        t = stack.popleft()

        if t[0] == "NODE_STRING":
            laststring = t[1]
            if lastpop and lastpop[0] == "NODE_STRING":
                deserialized[lastpop[1]] = t[1]
        elif t[0] == "NODE_OPENER":
            res = read_node(stack)
            deserialized[laststring] = res
        elif t[0] == "NODE_CLOSER":
            return deserialized
        elif t[0] == "NODE_COMMENT":
            continue

        lastpop = t

    return deserialized

def parse(stack):
    return read_node(stack)

def load(stream):
    res = parse(scan(stream))
    return res

def loads(string):
    return load(cStringIO.StringIO(string))
