#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

from aybu.website.models.base import Base
from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
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
        return "<SettingType %s>" % (self.name)


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
        return "<Setting %s (%s)>" % (self.name, self.raw_type)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).options(joinedload('type')).all()
