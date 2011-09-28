#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ©2010-present Asidev s.r.l. """

import re

all = ['boolify', 'urlify']

def boolify(value):
    return True if value.lower() in ('on', 'true', 'yes', 'ok', 'y') else False


def urlify(name):

    xlate = {
        0xc0: 'A', 0xc1: 'A', 0xc2: 'A', 0xc3: 'A', 0xc4: 'A', 0xc5: 'A',
        0xc6: 'Ae', 0xc7: 'C',
        0xc8: 'E', 0xc9: 'E', 0xca: 'E', 0xcb: 'E',
        0xcc: 'I', 0xcd: 'I', 0xce: 'I', 0xcf: 'I',
        0xd1: 'N',
        0xd2: 'O', 0xd3: 'O', 0xd4: 'O', 0xd5: 'O', 0xd6: 'O',
        0xd9: 'U', 0xda: 'U', 0xdb: 'U', 0xdc: 'U',
        0xdd: 'Y',
        0xe0: 'a', 0xe1: 'a', 0xe2: 'a', 0xe3: 'a', 0xe4: 'a', 0xe5: 'a',
        0xe6: 'ae', 0xe7: 'c',
        0xe8: 'e', 0xe9: 'e', 0xea: 'e', 0xeb: 'e',
        0xec: 'i', 0xed: 'i', 0xee: 'i', 0xef: 'i',
        0xf1: 'n',
        0xf2: 'o', 0xf3: 'o', 0xf4: 'o', 0xf5: 'o', 0xf6: 'o',
        0xf9: 'u', 0xfa: 'u', 0xfb: 'u', 0xfc: 'u',
        0xfd: 'y', 0xff: 'y'}

    url = name.strip()

    pattern = "\s"
    compiled = re.compile(pattern)
    m = compiled.search(url)
    while m:
        url = "%s%s%s" % (url[:m.start()], '_', url[m.end():])
        m = compiled.search(url)

    for char in url:
        code = ord(char)
        if code in xlate:
            url = url.replace(char, xlate[code])

    pattern = "[^a-zA-Z0-9_]"
    compiled = re.compile(pattern)
    m = compiled.search(url)
    while m:
        url = "%s%s" % (url[:m.start()], url[m.end():])
        m = compiled.search(url)

    url = url.lower()

    return url
