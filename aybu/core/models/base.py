#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.declarative import declarative_base
import logging


__all__ = ['Base']

log = logging.getLogger(__name__)


class AybuBase(object):

    @classmethod
    def on_attr_update(cls, obj, new, old, attr):

        if old == new:
            return old

        if not hasattr(obj, '_attrs_updates'):
            obj._attrs_updates = {}

        obj._attrs_updates[attr.key] = dict(old=old, new=new)

        return new

    @classmethod
    def count(cls, session, *filters):

        query = session.query(cls)

        for filter_ in filters:
            query = query.filter(filter_)

        return query.count()

    @classmethod
    def get(cls, session, pkey):
        obj = session.query(cls).get(pkey)
        if obj is None:
            raise NoResultFound("No obj with key {} in class {}"\
                                .format(pkey, cls.__name__))
        return obj

    @classmethod
    def all(cls, session, start=None, limit=None, query_options=()):
        query = session.query(cls).options(*query_options)
        return cls.slice_query(query, start, limit)

    @classmethod
    def first(cls, session):
        return session.query(cls).first()

    @classmethod
    def search(cls, session, filters=(), sort_by=None, sort_order='asc',
               start=None, limit=None, query_options=(), return_query=False):
        """ Perform or return a query which filters dataset using criterions
            specified by 'filters'.
        """
        if return_query and (start or limit):
            raise TypeError('Cannot use start or limit when returning query')

        query = session.query(cls).options(*query_options)

        try:
            for filter_ in filters:
                query = query.filter(filter_)

        except TypeError:
            # 'filters' is not an iterable.
            query = query.filter(filters)

        if sort_by:
            sort_by = getattr(cls, sort_by)
            sort_order = getattr(sort_by, sort_order)
            log.debug("Sorted by {}, {}".format(sort_by, sort_order))
            query = query.order_by(sort_order())

        if return_query:
            return query

        return cls.slice_query(query, start, limit)

    @classmethod
    def slice_query(cls, query, start=None, limit=None):

        if not start is None and not limit is None:
            end = start + limit
            #log.debug('query[%s:%s]. Start: %s. End: %s.', start, end)
            slice_ = query[start:end]

        elif not start is None and limit is None:
            #log.debug('query[%s:]. Start: %s.', start)
            slice_ = query[start:]

        elif start is None and not limit is None:
            #log.debug('query[:%s]. Limit: %s.', limit)
            slice_ = query[:limit]

        else:
            #log.debug('query.all(). Start: %s, Limit: %s', start, limit)
            slice_ = query.all()

        return slice_

    def delete(self, session=None):
        session = session if not session is None else object_session(self)
        session.delete(self)

    def to_dict(self, includes=(), excludes=()):
        """ Dictify entity.
        """
        if '__class__' not in excludes:
            dict_ = {'__class__': {'name': self.__class__.__name__,
                                   'module': self.__class__.__module__}}
        else:
            dict_ = {}

        for property_ in object_mapper(self).iterate_properties:

            if property_.key in excludes:
                continue

            if isinstance(property_, ColumnProperty):

                dict_[property_.key] = getattr(self, property_.key)

            elif isinstance(property_, RelationshipProperty) and \
                 property_.key in includes:

                if property_.uselist:
                    dict_[property_.key] = [item.to_dict()
                                            for item in getattr(self,
                                                                property_.key)]
                else:
                    dict_[property_.key] = getattr(self, property_.key).to_dict()

        return dict_

    dictify = to_dict
    #FIXME: this function will replace to_dict in the future!
    # Reason: to_dict was ported from LF aybu version.


Base = declarative_base(cls=AybuBase)
