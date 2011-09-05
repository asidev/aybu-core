#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

from aybu.website.models.base import Base
from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship


__all__ = []

log = getLogger(__name__)


class View(Base):

    __tablename__ = 'views'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    fs_view_path = Column(String(255), unique=True)

    def __repr__(self):
        return "<View %s (%s)>" % (self.name, self.fs_view_path)


class ViewDescription(Base):

    __tablename__ = 'views_descriptions'
    __table_args__ = (UniqueConstraint('view_id', 'lang_id'),
                      {'mysql_engine': 'InnoDB'})

    id = Column(Integer, primary_key=True)
    description = Column(UnicodeText, default=u'')
    view_id = Column(Integer, ForeignKey('views.id',
                                         onupdate='cascade',
                                         ondelete='cascade'))
    lang_id = Column(Integer, ForeignKey('languages.id',
                                         onupdate='cascade',
                                         ondelete='cascade'))

    view = relationship('View', backref='descriptions')
    language = relationship('Language')

    def __repr__(self):
        return "<ViewDescription %s>" % (self.description)
