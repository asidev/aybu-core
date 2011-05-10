#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

from aybu.cms.model.entities import Theme
from aybu.cms.model.meta import dbsession
from proxy import KeyValueCacheProxy
from exc import IntegrityError


class ThemesCacheProxy(KeyValueCacheProxy):

    def __new__(cls, prefix="themes"):
        return super(ThemesCacheProxy, cls).__new__(cls, prefix)

    def _get_all_keys(self):
        """ Called by the superclass __new__ to get all keys.
            Must return a list with string/unicode keys """
        return [r[0] for r in dbsession.query(Theme.name).distinct().all()]

    def _get_from_database(self, key):
        """ Called when superclass needs to get a setting from database using
            primary key. Must return a SQLA query """
        return Theme.query.filter(Theme.name == key).one().to_storage()

    def _back_from_cache(self, obj):
        return obj

    def _set_value(self, key, theme):
        raise IntegrityError("Cannot change themes")
