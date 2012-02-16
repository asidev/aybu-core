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
from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


__all__ = ['View', 'ViewDescription']

log = getLogger(__name__)


class View(Base):

    __tablename__ = 'views'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    id_seq = Sequence("{}_id_seq".format(__tablename__))
    id = Column(Integer, id_seq, primary_key=True)
    name = Column(Unicode(255), unique=True)
    fs_view_path = Column(String(255), unique=True)

    def __repr__(self):
        try:
            return "<View %s (%s)>" % (self.name, self.fs_view_path)
        except:
            return "<View>"

    @classmethod
    def all(cls, session, start=None, limit=None):
        query_options = (joinedload('descriptions'),
                         joinedload('descriptions.language'))
        return super(View, cls).all(session, start=start, limit=limit,
                                    query_options=query_options)

    @classmethod
    def get_by_name(cls, session, name):
        query_options = (joinedload('descriptions'),
                         joinedload('descriptions.language'))
        return super(View, cls).search(session,
                                       filters=(View.name == name,),
                                       start=0,
                                       limit=1,
                                       query_options=query_options)


class ViewDescription(Base):

    __tablename__ = 'views_descriptions'
    __table_args__ = (UniqueConstraint('view_id', 'lang_id'),
                      {'mysql_engine': 'InnoDB'})

    id_seq = Sequence("{}_id_seq".format(__tablename__))
    id = Column(Integer, id_seq, primary_key=True)
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
