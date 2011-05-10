#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import logging
from . proxies import SettingsCacheProxy, ThemesCacheProxy,\
                     LanguagesCacheProxy, MenusProxy
from http import purge_all_http

log = logging.getLogger(__name__)
__regions__ = ("pages", "languages", "settings", "themes", "resources",
               "menus", "nodes", "nodesinfo")
__all__ = ['flush_all', '__regions__', '__proxies__']


def flush_all(http=True):
    raise NotImplementedError
#    log.info("Flushing all regions in cache")
#    for region in __regions__:
#        log.debug("Flushing region '%s'", region)
#        cache.get_cache(region).clear()
#
#    # purge http before proxy as it needs some settings
#    if http:
#        purge_all_http()
#
#    ThemesCacheProxy().clear()
#    LanguagesCacheProxy().clear()
#    SettingsCacheProxy().clear()
#    MenusProxy().clear()





