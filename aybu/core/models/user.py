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
from aybu.core.models.types import Crypt
import crypt
from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import Table
from sqlalchemy.orm import (relationship,
                            joinedload)


__all__ = []

log = getLogger(__name__)


users_groups = Table('users_groups',
                     Base.metadata,
                     Column('users_username',
                            Unicode(255),
                            ForeignKey('users.username',
                                       onupdate="cascade",
                                       ondelete="cascade")),
                            Column('groups_name',
                                   Unicode(32),
                                   ForeignKey('groups.name',
                                              onupdate="cascade",
                                              ondelete="cascade")))


class User(Base):

    __tablename__ = 'users'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    username = Column(Unicode(255), primary_key=True)
    password = Column(Crypt(), nullable=False)

    groups = relationship('Group', secondary=users_groups, backref='users')

    @classmethod
    def get(cls, session, pkey):
        return session.query(cls).options(joinedload('groups')).get(pkey)

    @classmethod
    def check(cls, session, username, password):
        try:
            user = cls.get(session, username)
            enc_password = crypt.crypt(password, user.password[0:2])
            assert user.password == enc_password

        except:
            log.error('Invalid login: %s != %s', password, enc_password)
            raise ValueError('invalid username or password')

        else:
            return True


class Group(Base):

    __tablename__ = 'groups'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(32), primary_key=True)
