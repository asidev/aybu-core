#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""

import logging

from webhelpers.html import HTML
from webhelpers.html.builder import literal
from aybu.cms.model.entities import Node

from captchalib.helper import captcha

__all__ = ['captcha', 'url', 'form_input', 'locale_from_language', 'urlfy',
           'static_url']

log = logging.getLogger(__name__)


def url(url, *args, **kwargs):
    import inspect
    log.error("Called %s.url with params: '%s', '%s', '%s'",
                __name__, url, args, kwargs)
    try:
        frame = inspect.stack()[1]
#        info = inspect.getframeinfo(frame)
        log.error("Called from: %s'", frame)
        return url

    finally:
        del frame


def get_tree(root):
    return root.get_tree()


def get_menu(weight=1):
    return Node.root(weight).get_tree()


def form_input(name, title):
    fields = HTML.tag("label", title, for_=name)

    try:
        f = HTML.tag("input", '', id=name, name=name,
                     type='text', value=c.__getattr__(name))
    except:
        f = HTML.tag("input", '', id=name, name=name, type='text')
    fields = literal('%s%s' % (fields, f))

    try:
        f = HTML.tag("label", c.error[name], for_=name,
                     class_="error", generated="true")
        fields = literal('%s%s' % (fields, f))
    except:
        pass

    return fields


def locale_from_language(language, language_only=False):
    from babel import Locale
    try:
        if language_only:
            locale = Locale(language.lang.lower(), language.country.upper())
        else:
            locale = Locale(language.lang.lower(), language.country.upper())
        return locale
    except Exception:
        if language_only:
            lang = '%s %s' % (language.lang.lower(), language.country.upper())
        else:
            lang = '%s' % (language.lang.lower())
        message = 'Unable to create locale using %s' % (lang)
        log.exception(message)
        raise Exception(message)


def urlfy(name):

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
        0xfd: 'y', 0xff: 'y'
    }

    import re

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
    url = url.strip('_')

    return url


def static_url(resource_url):
    if resource_url.startswith('/uploads'):
        return resource_url

    return str('/static%s' % resource_url)
