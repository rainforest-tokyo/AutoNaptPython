
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------
# AutoNaptPython 
#
# Copyright (c) 2018 RainForest
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#-----------------------------------

import os
import sys
import json
import re
import traceback

ESCAPE_TABLE = [
    # 0      1        2        3        4        5        6        7        8        9        A        B        C        D        E        F
   #'\\x00', '\\x01', '\\x02', '\\x03', '\\x04', '\\x05', '\\x06', '\\a',   '\\b',   '\\t',   '\\n',   '\\v',   '\\f',   '\\r',   '\\x0e', '\\x0f',
    '\\x00', '\\x01', '\\x02', '\\x03', '\\x04', '\\x05', '\\x06', '\\x07', '\\x08', '\\t',   '\\n',   '\\b',   '\\x0c', '\r',    '\\x0e', '\\x0f',
    '\\x10', '\\x11', '\\x12', '\\x13', '\\x14', '\\x15', '\\x16', '\\x17', '\\x18', '\\x19', '\\x1a', '\\x1b', '\\x1c', '\\x1d', '\\x1e', '\\x1f',
    ' ',     '!',     '\\"',   '#',     '$',     '%',     '&',     "'",     '(',     ')',     '*',     '+',     ',',     '-',     '.',     '/',
    '0',     '1',     '2',     '3',     '4',     '5',     '6',     '7',     '8',     '9',     ':',     ';',     '<',     '=',     '>',     '?',
    '@',     'A',     'B',     'C',     'D',     'E',     'F',     'G',     'H',     'I',     'J',     'K',     'L',     'M',     'N',     'O',
    'P',     'Q',     'R',     'S',     'T',     'U',     'V',     'W',     'X',     'Y',     'Z',     '[',     '\\',     ']',     '^',    '_',
    '`',     'a',     'b',     'c',     'd',     'e',     'f',     'g',     'h',     'i',     'j',     'k',     'l',     'm',     'n',     'o',
    'p',     'q',     'r',     's',     't',     'u',     'v',     'w',     'x',     'y',     'z',     '{',     '|',     '}',     '~',     '\\x7f' ]

class Utils:
    @staticmethod
    def load_json(file):
        with open(file, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_json(file, obj):
        with open(file, 'w') as f:
            json.dump(obj, f)
            
    @staticmethod
    def get_string_from_bytes(bytes, enc):
        return bytes.decode(enc)

    @staticmethod
    def print_exception(ex):
        regex = re.compile('  File "([^"]+)", line ([0-9]+)(.*)')
        t, v, tb = sys.exc_info()

        print(str(ex))

        for i in traceback.format_exception(t, v, tb):
            line = i.rstrip()
            m = regex.match(line)

            if m is None:
                print('%s' % line)
            else:
                #print('%s' % line)
                print('  %s(%s): %s' % (m.group(1), m.group(2), m.group(3)))

    @staticmethod
    def assertion(cond, msg):
        regex = re.compile('  File "([^"]+)", line ([0-9]+)(.*)')

        if not cond:
            last = ''

            for i in traceback.format_stack():
                line = i.rstrip()
                m = regex.match(line)

                if m is not None:
                    s = '  %s(%s): %s' % (m.group(1), m.group(2), m.group(3))

                    if s.endswith('in assertion') or s.endswith('in expects_type'):
                        pass
                    else:
                        last = s

            print('%s -- assertion failed' % last)

            assert False, msg

    @staticmethod
    def expects_type(cls, obj, name, allow_none = False):
        if allow_none and obj is None:
            return

        Utils.assertion(isinstance(obj, cls), '%s: expects type %s' % (name, cls.__name__))

    @staticmethod
    def get_escaped_string(data):
        #s       = Utils.get_string_from_bytes(data[offset:offset+size], 'ascii')
        #s       = s.encode('string-escape')
        #return s
        a = []

        for i in data:
            a.append(ESCAPE_TABLE[i] if i < 0x80 else '\\x%02x' % i)

        return ''.join(a)

    @staticmethod
    def is_windows(name):
        return name == 'nt'

    @staticmethod
    def is_linux(name):
        return name == 'posix'
