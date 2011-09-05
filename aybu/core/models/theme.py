#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """


from aybu.website.models.base import Base
from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Table
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship


__all__ = ['Keyword', 'Theme']

log = getLogger(__name__)


class Keyword(Base):

    __tablename__ = 'keywords'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(64), primary_key=True)

    _used_by_table = Table('node_infos__keywords',
                           Base.metadata,
                           Column('node_infos_id',
                                  Integer,
                                  ForeignKey('node_infos.id',
                                             onupdate="cascade",
                                             ondelete="cascade")),
                                  Column('keyword_name',
                                         Unicode(64),
                                         ForeignKey('keywords.name',
                                                    onupdate="cascade",
                                                    ondelete="cascade")))
    used_by = relationship('NodeInfo',
                           secondary=_used_by_table,
                           backref=backref('keywords'))


class Theme(Base):

    __tablename__ = 'themes'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(128), primary_key=True)
    parent_name = Column(Unicode(128), ForeignKey('themes.name'))
    children = relationship('Theme',
                            backref=backref('parent', remote_side=name))
