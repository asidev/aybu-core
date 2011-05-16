#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

import logging
import sqlalchemy.orm.session
import sqlalchemy.exc
from beaker.cache import CacheManager

from exc import IntegrityError
from aybu.cms.model.meta import dbsession, session_cache_extension

log = logging.getLogger(__name__)


class CacheProxy(object):
    cache_manager = None
    cache_settings = None

    @classmethod
    def init_cache(settings):
        raise NotImplementedError

    def __new__(cls, prefix):
        obj = super(CacheProxy, cls).__new__(cls)
        object.__setattr__(obj, "prefix", prefix)
        object.__setattr__(obj, "log", logging.getLogger(cls.__name__))
        if CacheProxy.cache_settings and not CacheProxy.cache_manager:
            log.info("Creating cache manager for proxies")
            mgr = CacheManager(**CacheProxy.cache_settings)
            CacheProxy.cache_manager = mgr
        if CacheProxy.cache_manager:
            object.__setattr__(obj, "_cache",
                               CacheProxy.cache_manager.get_cache(prefix))
        else:
            object.__setattr__(obj, "_cache", None)
        return obj

    def _get_from_database(self, key):
        raise NotImplementedError

    def _get_from_cache(self, key):

        hot = True

        def load_from_db():
            global hot
            self.log.info("[%s] loading key '%s' from database", self, key)
            obj = self._get_from_database(unicode(key))
            hot = False
            return obj

        #if 'cache_disabled' in config and not config['cache_disabled']:
        if self._cache:
            obj = self._cache.get_value(key=key, createfunc=load_from_db)
            if hot:
                self.log.debug("[%s] got key '%s' from cache", self, key)
                obj = self._back_from_cache(obj)
            return obj
        else:
            self.log.debug("[%s] Cache is disabled, getting key '%s' "
                          "from database", self, key)
            return load_from_db()

    def _back_from_cache(self, obj):
        try:
            # get the object session and ensure that is the same as dbsession
            # this will raise
            session = sqlalchemy.orm.session.object_session(obj)
            if not session:
                raise sqlalchemy.exc.InvalidRequestError()
            if obj not in dbsession:
                self.log.debug("[%s] object %s is attacched to another "
                               "session, detaching", self, obj)
                session.expunge(obj)
                raise sqlalchemy.exc.InvalidRequestError()

        except sqlalchemy.exc.InvalidRequestError:
            try:
                obj = dbsession.merge(obj, load=False)
                self.log.debug("[%s] merged back %s in session", self, obj)
            except sqlalchemy.orm.exc.UnmappedInstanceError:
                self.log.debug("[%s] %s is not mapped to any SQLA session",
                               self, obj)
        return obj

    def purge(self, key):
        self.log.debug("[%s] Purging key '%s' from cache", self.prefix, key)
        if self._cache:
            self._cache.remove_value(key)
            del self._cache[key]

    def clear(self):
        self.log.info("[%s] Clearing cache", self)
        if self._cache:
            self._cache.clear()


class SingletonProxy(CacheProxy):
    _instances = dict()

    def __new__(cls, prefix, id=None, register=True, oncreate=None):
        # Keep all instances as singletons per-id,
        # so we construct max one instance for each id given
        id = "{0}_{1}".format(prefix, id) if id else prefix
        if id not in cls._instances:
            log.debug("Calling __new__ on object for id '%s' "
                      "for class %s", id, cls.__name__)
            log.info("Created proxy for prefix '%s'", prefix)
            obj = super(SingletonProxy, cls).__new__(cls, prefix)
            # run the oncreate callback
            if oncreate:
                obj = oncreate(obj)
            # add object to the list of singletons
            cls._instances[id] = obj
            if register:
                # Register with the session so we can properly handle
                # the *_commit and *_rollback events
                session_cache_extension.register(obj)

        return cls._instances[id]

    def __str__(self):  # pragma: nocover
        return "<%s>" % (self.__class__.__name__)

    def __repr__(self):  # pragma: nocover
        return "<%s %s>" % (self.__class__.__name__, self._values)


class KeyValueCacheProxy(SingletonProxy):

    def __new__(cls, prefix, iterable=True):
        obj = super(KeyValueCacheProxy, cls).__new__(cls, prefix)
        object.__setattr__(obj, "_values", dict())
        object.__setattr__(obj, "_updated", [])
        object.__setattr__(obj, "iterable", iterable)
        obj.reload_keys()
        return obj

    def reload_keys(self):
        if self._cache:
            self._keys = self._cache.get_value(
                               key="keys",
                               createfunc=self._get_all_keys_wrapper
                         )
        else:
            self._keys = self._get_all_keys_wrapper()

    # wrappers
    def _get_all_keys_wrapper(self):
        self.log.debug("[%s]: Getting all keys from database", self)
        return self._get_all_keys()

    def _set_value_wrapper(self, key, value):
        self.log.debug("[%s] Updating key '%s' in database with value '%s'",
                       self, key, value)
        self._set_value(key, value)

    # This methods must be redefined in subclasses
    def _set_value(self, key, value):
        raise NotImplementedError

    def _get_all_keys(self):
        raise NotImplementedError

    # private methods
    def _get_value(self, key):
        if key not in self._values:
            self._values[key] = self._get_from_cache(key)

        self._values[key] = self._back_from_cache(self._values[key])
        return self._values[key]

    # Public methods
    def clear_locals(self):
        self._values = dict()

    def purge(self, key):
        if key in self._values:
            del self._values[key]
        super(KeyValueCacheProxy, self).purge(key)

    def purge_updated_keys(self):
        self.log.debug("[%s] Purging updated keys: %s", self, self._updated)
        for key in self._updated:
            self.purge(key)

    def clear_updated_keys(self):
        self.log.debug("[%s] Clearing updated keys: %s", self, self._updated)
        for key in self._updated:
            if key in self._values:
                del self._values[key]
        self._updated = []

    def clear(self):
        super(KeyValueCacheProxy, self).clear()
        self.clear_locals()

    # dict-like access
    def __getitem__(self, index):
        return self._get_value(index)

    def __setitem__(self, key, value):
        if key not in self._values:
            self._get_value(key)

        self._values[key] = value
        self._updated.append(key)
        self.log.debug("[%s]: object updated: %s", self, self._updated)
        self._set_value_wrapper(key, value)

    def __delitem__(self, key):
        raise IntegrityError("Cannot delete keys from a cache proxy object")

    def __len__(self):
        return len(self._keys)

    # iterators
    def __iter__(self):
        if not self.iterable:
            raise TypeError("'%s' object is not iterable",
                            self.__class__.__name__)
        return iter(self._keys)

    def iteritems(self):
        if not self.iterable:
            raise AttributeError("iteritems")
        return ((k, self[k]) for k in self)

    def values(self):
        if not self.iterable:
            raise AttributeError("value")
        return [self[k] for k in self]

    def keys(self):
        if not self.iterable:
            raise AttributeError("keys")
        return list(self._keys)
