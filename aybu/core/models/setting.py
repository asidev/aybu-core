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

import ast
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
    raw_value = Column(Unicode(512), name='value', nullable=False)
    ui_administrable = Column(Boolean, default=False)

    type_name = Column(Unicode(64), ForeignKey('setting_types.name',
                                               onupdate='cascade',
                                               ondelete='restrict'))

    type = relationship('SettingType', backref='settings')

    def __init__(self, **kwargs):
        if "raw_value" in kwargs:
            kwargs.pop('value', '')
            kwargs['raw_value'] = unicode(kwargs['raw_value'])
        else:
            try:
                value = kwargs.pop('value')
                kwargs['raw_value'] = value

            except KeyError:
                # FIXME is NameError correct?
                raise NameError('__init__ has not arg "value"')

        try:
            self._get_cast(type_=kwargs['type'])(kwargs['raw_value'])

        except KeyError:
            raise NameError('__init__ has no arg "type"')

        except:
            raise ValueError('Invalid value %s for type %s' %
                             (kwargs['raw_value'], kwargs['type'].raw_type))

        super(Setting, self).__init__(**kwargs)


    def _get_cast(self, type_=None):
        def noop(value):
            return value

        if type_ is None:
            type_ = self.type

        if not hasattr(self, '_caster'):
            if type_.raw_type == 'unicode':
                self._caster = noop
            elif type_.raw_type == 'bool':
                self._caster = ast.literal_eval
            else:
                self._caster = eval(type_.raw_type)

        return self._caster

    @property
    def value(self):
        return self._get_cast()(self.raw_value)

    @value.setter
    def value(self, v):
        # try to convert first
        try:
            self._get_cast()(v)
            self.raw_value = unicode(v)
        except:
            raise ValueError("v must be of type %s"  % (self.type.raw_type))

    def __repr__(self):
        return "<Setting %s (%s)>" % (self.name, self.value)

    @classmethod
    def all(cls, session, start=None, limit=None):
        # query_options must not be in the method signature:
        # the user should not use SQLA internals.
        return super(Setting, cls).all(session, start=start, limit=limit,
                                       query_options=(joinedload('type'),))

    @classmethod
    def count(cls, session, ui_administrable=False):
        """ Count settings in the collection:
            count UI administrable settings only when ui_adminstrable == True.
        """
        return super(Setting, cls).count(session,
                                         Setting.ui_administrable == True)

    @classmethod
    def list(cls, session, ui_administrable=False, 
             sort_by=None, sort_order='asc', start=None, limit=None):
        return super(Setting, cls).search(session,
                                          Setting.ui_administrable == True,
                                          sort_by=sort_by,
                                          sort_order=sort_order,
                                          start=start,
                                          limit=limit,
                                          query_options=(joinedload('type'),))

    def to_dict(self):
        return dict(name=self.name,
                    value=self.value,
                    raw_type=self.type.raw_type,
                    ui_administrable=self.ui_administrable,
                    setting_type_name=self.type.name)
