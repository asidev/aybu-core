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


from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.sql.expression


__all__ = ['Base']


class AybuBase(object):

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
        return get_sliced(query, start, limit)

    @classmethod
    def first(cls, session):
        return session.query(cls).first()

    @classmethod
    def search(cls, session, filters=(), sort_by=None, sort_order='asc',
               start=None, limit=None, query_options=(), return_query=False):
        """ Perform or return a query which filters dataset using criterions
            specified by 'filters'.
        """
        query = session.query(cls).options(*query_options)

        try:
            for filter_ in filters:
                query = query.filter(filter_)
        except TypeError as e:
            # 'filters' is not an iterable.
            query = query.filter(filters)

        if sort_by:
            sort_order = getattr(sqlalchemy.sql.expression, sort_order)
            query = query.order_by(sort_order(sort_by))

        if return_query:
            return query

        return get_sliced(query, start, limit)

    def delete(self, session=None):
        session = session if not session is None else object_session(self)
        session.delete(self)


Base = declarative_base(cls=AybuBase)


def get_sliced(query, start=None, limit=None):

    if not start is None and not limit is None:
        return query[start:start + limit]

    if not start is None:
        return query[start:]

    return query.all()
