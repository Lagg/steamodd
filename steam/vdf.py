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

STRING = '"'
NODE_OPEN = '{'
NODE_CLOSE = '}'
COMMENT = '/'
CR = '\r'
LF = '\n'

def _symtostr(line, i):
    opening = i + 1
    closing = 0

    ci = line.find('"', opening)
    while ci != -1:
        if line[ci - 1] != '\\':
            closing = ci
            break
        ci = line.find('"', ci + 1)

    finalstr = line[opening:closing]
    return finalstr, i + len(finalstr) + 1

def _parse(stream, ptr = 0):
    i = ptr
    laststr = None
    lasttok = None
    deserialized = {}

    while i < len(stream):
        c = stream[i]

        if c == STRING:
            string, i = _symtostr(stream, i)
            if lasttok == STRING:
                deserialized[laststr] = string
            laststr = string
        elif c == NODE_OPEN:
            deserialized[laststr], i = _parse(stream, i + 1)
        elif c == NODE_CLOSE:
            return deserialized, i
        elif c == COMMENT:
            if (i + 1) < len(stream) and stream[i + 1] == '/':
                i = stream.find('\n', i)
        elif c == CR or c == LF:
            ni = i + 1
            if ni < len(stream) and stream[ni] == LF:
                i = ni
            if lasttok != LF:
                c = LF
        else:
            c = lasttok

        lasttok = c
        i += 1

    return deserialized, i

def _run_parse_encoded(string):
    encoded = string
    try:
        encoded = str.decode(encoded, "utf-16")
    except:
        pass

    res, ptr = _parse(encoded)
    return res

def load(stream):
    return _run_parse_encoded(stream.read())

def loads(string):
    return _run_parse_encoded(string)
