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

from aybu.core.models.base import Base
from sqlalchemy import (Column,
                        Unicode,
                        or_)
from aybu.core.testing import TransactionalTestsBase
from sqlalchemy.orm.exc import NoResultFound
import sqlalchemy.orm.query
import sqlalchemy.sql.expression


class Entity(Base):
    __tablename__ = 'entities'
    __table_args__ = ({'mysql_engine': 'InnoDB'})
    name = Column(Unicode(32), primary_key=True)


class BaseTests(TransactionalTestsBase):

    @classmethod
    def setUpClass(cls):
        super(BaseTests, cls).setUpClass()
        cls.create_tables(drop=True)

    def setUp(self):
        super(BaseTests, self).setUp()
        self.session.add(Entity(name='first'))
        self.session.add(Entity(name='second'))
        self.session.add(Entity(name='third'))
        self.session.add(Entity(name='fourth'))
        self.session.add(Entity(name='fifth'))
        self.session.flush()

    def test_count(self):
        self.assertEqual(Entity.count(self.session), 5)
        self.assertEqual(Entity.count(self.session,
                                      Entity.name == 'first'), 1)

        self.assertEqual(Entity.count(self.session,
                                      Entity.name == 'first'), 1)
        self.assertEqual(Entity.count(self.session,
                                      or_(Entity.name == 'first',
                                          Entity.name == 'second')),
                                      2)

    def test_get(self):
        self.assertRaises(NoResultFound, Entity.get, self.session, 'unknown')
        self.assertTrue(self.session.query(Entity).get('first') is
                        Entity.get(self.session, 'first'))

    def test_all(self):
        self.assertEqual(len(Entity.all(self.session)), 5)

    def test_first(self):
        self.assertTrue(self.session.query(Entity).first() is
                        Entity.first(self.session))

    def test_search(self):
        res = Entity.search(self.session, filters=(Entity.name == 'first'),)
        self.assertEqual(type(res), list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].name, 'first')

    def test_search_start_limit(self):
        res1 = Entity.all(self.session)
        res2 = Entity.search(self.session, start=2, limit=2)
        self.assertEqual(len(res2), 2)
        self.assertTrue(res2[0] is res1[2])
        self.assertTrue(res2[1] is res1[3])

    def test_search_query(self):
        res_all = Entity.all(self.session)
        self.assertRaises(TypeError, Entity.search, self.session,
                            return_query=True, start=2, limit=2)
        res = Entity.search(self.session, return_query=True)
        self.assertEqual(type(res), sqlalchemy.orm.query.Query)
        self.assertEqual(res.count(), 5)
        self.assertEqual(res[2], res_all[2])
        self.assertEqual(res[2:3], res_all[2:3])
        self.assertEqual(res[2:], res_all[2:])

    def test_sort(self):
        for sort_by in ('asc', 'desc'):
            sort_order = getattr(sqlalchemy.sql.expression, sort_by)
            sorted_ = self.session.query(Entity)\
                        .order_by(sort_order(Entity.name)).all()
            self.assertEqual(sorted_, Entity.search(self.session,
                                                    sort_by='name',
                                                    sort_order=sort_by))

    def test_delete(self):
        first = Entity.get(self.session, 'first')
        first.delete()
        self.session.flush()
        self.assertNotIn('first', (e.name for e in Entity.all(self.session)))
