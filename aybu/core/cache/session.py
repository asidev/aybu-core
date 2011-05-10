#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

import logging
from sqlalchemy.orm import SessionExtension


class PurgeSessionExtension(SessionExtension):

    def __init__(self):
        self.proxies = dict()
        self.log = logging.getLogger(__name__)
        self.log.info("Created PurgeSessionExtension")

    def register(self, proxy):
        self.log.debug("Registered proxy %s", proxy)
        self.proxies[proxy.prefix] = proxy

    def purge_updated(self):
        for proxy in self.proxies.values():
            if hasattr(proxy, "purge_updated_keys"):
                proxy.purge_updated_keys()

    def clear_updated(self):
        for proxy in self.proxies.values():
            if hasattr(proxy, "clear_updated_keys"):
                proxy.clear_updated_keys()

    def before_commit(self, session):
        self.log.debug("before_commit: Purging modified keys in cache")
        self.purge_updated()

    def after_commit(self, session):
        self.log.debug("after_commit: Purging modified keys in cache")
        self.purge_updated()
        self.log.debug("after_commit: Clearing updated keys in proxies")
        self.clear_updated()

    def after_rollback(self, session):
        self.log.debug("after_rollback: Clearing updated keys in proxies")
        self.clear_updated()

    def after_begin(self, session, transaction, rollback):
        self.log.debug("after_begin: clearing values in local dictionaries")
        for proxy in self.proxies.values():
            if hasattr(proxy, "clear_locals"):
                proxy.clear_locals()
