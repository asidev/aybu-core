#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

from aybu.core.models import Base
from aybu.core.models import Page
from aybu.core.utils.exceptions import ConstraintError
from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


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
    def check_max_pages(cls, session):
        """ Raise an exception when the number of pages in the database
            is greater or equal then 'max_pages' setting.

            Query:
            SELECT count(?) AS count_1
            FROM settings WHERE settings.name = ? AND
                 settings.value < (SELECT count(nodes.id) AS count_2
                                   FROM nodes
                                   WHERE nodes.row_type IN (?))

        """
        n_pages = session.query(func.count(Page.id)).subquery()
        q = session.query(func.count('*')).filter(Setting.name=='max_pages')
        q = q.filter(n_pages >= Setting.value)

        if q.scalar():
            raise ConstraintError('Setting.max_pages')
