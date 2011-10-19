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

from aybu.core.models import Base
from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import relationship


__all__ = ['Setting', 'SettingType']

log = getLogger(__name__)


class SettingType(Base):

    __tablename__ = 'setting_types'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(64), primary_key=True)
    raw_type = Column(String(8), nullable=False)

    def __repr__(self):
        return "<SettingType %s (%s)>" % (self.name, self.raw_type)


class Setting(Base):

    __tablename__ = 'settings'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(128), primary_key=True)
    value = Column(Unicode(512), nullable=False)
    ui_administrable = Column(Boolean, default=False)

    type_name = Column(Unicode(64), ForeignKey('setting_types.name',
                                               onupdate='cascade',
                                               ondelete='restrict'))

    type = relationship('SettingType', backref='settings')

    def __repr__(self):
        return "<Setting %s (%s)>" % (self.name, self.value)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).options(joinedload('type')).all()

    @classmethod
    def get(cls, session, name):
        return session.query(cls).filter(cls.name == name).one()
