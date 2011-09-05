#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

from aybu.website.models.base import Base
from aybu.website.models.types import SHA1
from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import Table
from sqlalchemy.orm import relationship


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
    password = Column(SHA1(), nullable=False)

    groups = relationship('Group', secondary=users_groups, backref='users')


class Group(Base):

    __tablename__ = 'groups'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(32), primary_key=True)
