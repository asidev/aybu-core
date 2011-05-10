#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

from aybu.core.model.entities import Language
from aybu.core.model.meta import dbsession
from proxy import KeyValueCacheProxy


class LanguagesCacheProxy(KeyValueCacheProxy):

    def __new__(cls, prefix="languages"):
        return super(LanguagesCacheProxy, cls).__new__(cls, prefix)

    def _get_all_keys(self):
        """ Called by the superclass __new__ to get all keys.
            Must return a list with string/unicode keys """
        return ["%s_%s" % (lang, country)
                for lang, country in
                dbsession.query(Language.lang, Language.country).\
                                distinct().order_by(Language.id).all()]

    def get_by(self, lang, country):
        return self["%s_%s" % (lang, country)]

    @property
    def all(self):
        return [l for l in self]

    @property
    def first(self):
        return self[self._keys[0]]

    @property
    def enabled(self):
        return [l for l in self if l.enabled]

    def enable(self, index):
        self.log.debug("[%s] Enabling language %s",
                       self.__class__.__name__, self[index])
        self[index] = True

    def disable(self, index):
        self.log.debug("[%s] Disabling language %s",
                       self.__class__.__name__, self[index])
        self[index] = False

    def _get_from_database(self, key):
        """ Called when superclass needs to get a setting from database using
            primary key. Must return a SQLA query """
        lang, country = key.split("_")
        return Language.query.filter(Language.lang == lang)\
               .filter(Language.country == country)\
               .one()

    def __iter__(self):
        # load all entries
        return iter([self[k] for k in self._keys])

    def __contains__(self, lang):
        try:
            self[lang]
            return True
        except KeyError:
            return False

    def __getitem__(self, index):
        if isinstance(index, int):
            index = self._keys[index]
        elif isinstance(index, Language):
            index = "%s_%s" % (index.lang, index.country)
        return super(LanguagesCacheProxy, self).__getitem__(index)

    def __setitem__(self, index, value):
        if isinstance(index, Language):
            index = "%s_%s" % (index.lang, index.country)

        l = self[index]
        l.enabled = value
        super(LanguagesCacheProxy, self).__setitem__(index, l)

    def _set_value(self, key, lang):
        self._get_from_database(key).enabled = lang.enabled
