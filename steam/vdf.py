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
BR_OPEN = '['
BR_CLOSE = ']'
COMMENT = '/'
CR = '\r'
LF = '\n'
SPACE = ' '
TAB = '\t'
WHITESPACE = set(' \t\r\n')

try:
    from collections import OrderedDict as odict
except ImportError:
    odict = dict

def _symtostr(line, i, token = STRING):
    opening = i + 1
    closing = 0

    ci = line.find(token, opening)
    while ci != -1:
        if line[ci - 1] != '\\':
            closing = ci
            break
        ci = line.find(token, ci + 1)

    finalstr = line[opening:closing]
    return finalstr, i + len(finalstr) + 1

def _unquotedtostr(line, i):
    ci = i
    _len = len(line)
    while ci < _len:
        if line[ci] in WHITESPACE:
            break
        ci += 1
    return line[i:ci], ci

def _parse(stream, ptr = 0):
    i = ptr
    laststr = None
    lasttok = None
    lastbrk = None
    deserialized = {}

    while i < len(stream):
        c = stream[i]

        if c == NODE_OPEN:
            deserialized[laststr], i = _parse(stream, i + 1)
        elif c == NODE_CLOSE:
            return deserialized, i
        elif c == BR_OPEN:
            lastbrk, i = _symtostr(stream, i, BR_CLOSE)
        elif c == COMMENT:
            if (i + 1) < len(stream) and stream[i + 1] == '/':
                i = stream.find('\n', i)
        elif c == CR or c == LF:
            ni = i + 1
            if ni < len(stream) and stream[ni] == LF:
                i = ni
            if lasttok != LF:
                c = LF
        elif c != SPACE and c != TAB:
            string, i = (
                _symtostr if c == STRING else
                _unquotedtostr)(stream, i)
            if lasttok == STRING:
                if laststr in deserialized and lastbrk is not None:
                    # ignore this entry if it's the second bracketed expression
                    lastbrk = None
                else:
                    deserialized[laststr] = string
            # force c = STRING so that lasttok will be set properly
            c = STRING
            laststr = string
        else:
            c = lasttok

        lasttok = c
        i += 1

    return deserialized, i

def _run_parse_encoded(string):
    try:
        encoded = string.encode("ascii")
    except UnicodeDecodeError:
        encoded = string.encode("utf-16")

    res, ptr = _parse(encoded)
    return res

def load(stream):
    return _run_parse_encoded(stream.read())

def loads(string):
    return _run_parse_encoded(string)

indent = 0
mult = 2
def _i():
    return ' ' * (indent * mult)

def _dump(obj):
    nodefmt = unicode('\n' + _i() + '"{0}"\n' + _i() + '{{\n{1}' + _i() + '}}\n\n')
    podfmt = unicode(_i() + '"{0}" "{1}"\n')
    lstfmt = unicode(_i() + (' ' * mult) + '"{0}" "1"')
    global indent

    indent += 1

    nodes = []
    for k, v in obj.iteritems():
        if isinstance(v, dict):
            nodes.append(nodefmt.format(k, _dump(v)))
        else:
            try:
                try:
                    v.isdigit
                    nodes.append(podfmt.format(k, v))
                except AttributeError:
                    lst = map(lstfmt.format, v)
                    nodes.append(nodefmt.format(k, '\n'.join(lst) + '\n'))
            except TypeError:
                nodes.append(podfmt.format(k, v))

    indent -= 1

    return unicode(''.join(nodes))

def _run_dump(obj):
    res = _dump(obj)
    return res.encode("utf-16")

def dump(obj, stream):
    stream.write(_run_dump(obj))

def dumps(obj):
    return _run_dump(obj)
