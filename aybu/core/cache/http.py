#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""
import logging

from httpcachepurger import HTTPCachePurger
from aybu.core.cache.proxies import SettingsCacheProxy

log = logging.getLogger(__name__)


def purge_http(request, paths=None):
    s = SettingsCacheProxy()
    log.debug("proxy_enabled: %s, (type: %s)", s['proxy_enabled'],
              str(type(s['proxy_enabled'])))
    if not s['proxy_enabled']:
        log.debug("Not purging HTTP cache as proxy is disabled")
        return

    # FIXME: check environ
    hostname = request.environ['HTTP_HOST']
    if not paths:
        paths = [request.environ['PATH_INFO']]
    elif isinstance(paths, basestring):
        paths = [paths]
    server = s['proxy_address']
    port = s['proxy_port']
    purger = HTTPCachePurger(hostname, server, port, strict=True,
                             timeout=s['proxy_purge_timeout'])
    purger.purge(paths)


def purge_all_http():
    purge_http("^/.*")
