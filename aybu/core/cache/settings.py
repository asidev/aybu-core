#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

import ast
from aybu.cms.model.entities import Setting
from aybu.cms.model.meta import dbsession
from proxy import KeyValueCacheProxy


class SettingsCacheProxy(KeyValueCacheProxy):

    def __new__(cls, prefix="settings"):
        return super(SettingsCacheProxy, cls).__new__(cls, prefix)

    def _get_all_keys(self):
        """ Called by the superclass __new__ to get all keys.
            Must return a list with string/unicode keys """
        return [r[0] for r in dbsession.query(Setting.name).distinct().all()]

    def _get_from_database(self, key):
        """ Called when superclass needs to get a setting from database using
            primary key. Must return a SQLA query """
        return Setting.query.filter(Setting.name == key).one()

    def _set_value(self, key, setting):
        """ Called when superclass need to set a value in database.
            setting the new modified Storage """
        Setting.query.filter(Setting.name == key).one().value = setting.value

    def __getitem__(self, index):
        v = super(SettingsCacheProxy, self).__getitem__(index)
        if v.raw_type != "unicode":
            if v.raw_type == "bool":
                value = ast.literal_eval(str(v.value))
            else:
                value = eval(v.raw_type)(v.value)
        else:
            value = v.value
        return value

    def __setitem__(self, index, value):
        s = self._get_value(index)
        s.value = unicode(value)
        super(SettingsCacheProxy, self).__setitem__(index, s)

    def getobj(self, key):
        return self._get_value(key)

    def __getattr__(self, attr):
        return self[attr]
