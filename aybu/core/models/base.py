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


__all__ = ['Base']


class AybuBase(object):

    @classmethod
    def count(cls, session, filters=[]):
        query = session.query(cls)
        try:
            for filter_ in filters:
                query = query.filter(filter_)
        except TypeError:
                query = query.filter(filters)

        return query.count()

    @classmethod
    def get(cls, session, pkey):
        obj = session.query(cls).get(pkey)
        if obj is None:
            raise NoResultFound("No {} in {}".format(pkey, cls.__name__))
        return obj

    @classmethod
    def all(cls, session):
        return session.query(cls).all()

    def delete(self):
        object_session(self).delete(self)


Base = declarative_base(cls=AybuBase)


def get_sliced(query, start=None, limit=None):

    if not start is None and not limit is None:
        return query[start:start + limit]

    if not start is None:
        return query[start:]

    return query.all()
