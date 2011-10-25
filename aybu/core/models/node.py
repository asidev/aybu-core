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

from aybu.core.utils.modifiers import boolify
from aybu.core.utils.exceptions import ValidationError
from aybu.core.models.base import Base, get_sliced
from aybu.core.models.view import View
from aybu.core.models.setting import Setting
from logging import getLogger
from sqlalchemy import and_
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import UniqueConstraint
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast
import warnings


__all__ = []


log = getLogger(__name__)


class Node(Base):

    __tablename__ = 'nodes'
    __table_args__ = (UniqueConstraint('parent_id', 'weight'),
                      {'mysql_engine': 'InnoDB'})

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=True)
    hidden = Column(Boolean, default=False)
    weight = Column(Integer, nullable=False)

    parent_id = Column(Integer, ForeignKey('nodes.id'))
    children = relationship('Node', backref=backref('parent', remote_side=id),
                            primaryjoin='Node.id == Node.parent_id')

    discriminator = Column('row_type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    @property
    def type(self):
        return self.__class__.__name__

    def __repr__(self):
        parent_id = None if self.parent is None else self.parent.id
        return '<%s id="%s" parent="%s" weight="%s" />' % (self.type,
                                                           self.id,
                                                           parent_id,
                                                           self.weight)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def get_by_id(cls, session, id_):
        return cls.get(session, id_)

    @classmethod
    def get_by_enabled(cls, session, enabled, start=None, limit=None):
        query = session.query(cls).filter(cls.enabled == enabled)
        return get_sliced(query, start, limit)

    @classmethod
    def get_max_weight(cls, session, **params):
        q = session.query(func.max(cls.weight))
        q = q.filter(cls.parent == params['parent'])
        return  q.scalar()

    @validates('parent')
    def validate_parent(self, key, value):
        if isinstance(self, Menu):
            if value != None:
                raise ValidationError()
        else:
            if not isinstance(value, (Menu, Section, Page)):
                raise ValidationError()
        return value

    @validates('children')
    def validate_children(self, key, value):
        if isinstance(self, (ExternalLink, InternalLink)):
            if value != None or value != []:
                raise ValidationError()
        return value

    @classmethod
    def create(cls, session, **params):
        """ Create a persistent 'cls' object and return it."""
        warnings.warn("Node.create is in pending removal", DeprecationWarning)

        if cls == Node:
            raise ValidationError('cls: Node creation is not allowed!')
        entity = cls(**params)
        session.add(entity)
        return entity

    def get_translation(self, session, lang):
        from aybu.core import models

        info_class = getattr(models, '%sInfo' % self.__class__.__name__)
        query = session.query(info_class).filter(info_class.node == self)\
                                         .filter(info_class.lang == lang)
        try:
            return query.one()
        except:
            return None


class Menu(Node):

    __mapper_args__ = {'polymorphic_identity': 'menu'}


node_banners = Table('nodes_banners__files',
                     Base.metadata,
                     Column('nodes_id',
                            Integer,
                            ForeignKey('nodes.id',
                                       onupdate="cascade",
                                       ondelete="cascade")),
                     Column('files_id',
                            Integer,
                            ForeignKey('files.id',
                                       onupdate="cascade",
                                       ondelete="cascade")))


class Page(Node):

    __mapper_args__ = {'polymorphic_identity': 'page'}

    home = Column(Boolean, default=False)
    sitemap_priority = Column(Integer, default=50)
    banners = relationship('Banner', secondary=node_banners)

    view_id = Column(Integer, ForeignKey('views.id',
                                         onupdate='cascade',
                                         ondelete='restrict'))
    view = relationship('View')

    @classmethod
    def set_homepage(cls, session, page):
        session.query(cls).update(dict(home=False))
        session.query(cls).filter(cls.id == page.id).update(dict(home=True))

    @classmethod
    def get_homepage(cls, session):
        try:
            return session.query(cls).filter(cls.home == True).one()
        except NoResultFound as e:
            log.debug(e)

        query = session.query(func.min(Page.weight).label('min_weight'))
        criterion = Page.parent.has(and_(Menu.weight == 1,
                                         Menu.parent == None))

        query = query.filter(criterion).group_by(Page.parent)

        criterion = and_(Page.parent.has(and_(Menu.weight == 1,
                                              Menu.parent == None)),
                         Page.weight == query.subquery())
        query = session.query(Page).filter(criterion)
        try:
            homepage = query.one()
        except NoResultFound:
            homepage = session.query(Page).first()

        homepage.home = True

        return homepage

    @validates('view')
    def validate_view(self, key, value):
        if value is None:
            raise ValidationError()

        # The following control should be already checked by sqlalchemy when
        # the object is added to the session
        if not isinstance(value, View):
            raise ValidationError()

        return value

    @validates('sitemap_priority')
    def validate_sitemap_priority(self, key, value):
        if value > 100 or value < 1:
            # CHECK
            # We can set the default value or raise the exception
            raise ValidationError()
        return value

    @validates('home')
    def validate_home(self, key, value):
        if not isinstance(value, bool):
            value = boolify(value)
        return value

    @classmethod
    def is_last_page(cls, session):
        return True if session.query(cls).count() == 1 else False

    @classmethod
    def new_page_allowed(cls, session):
        """
        num_pages = session.query(cls).count()
        max_pages = session.query(Setting).filter(Setting.name==u'max_pages').\
                            one()['value']
        return not (num_pages >= max_pages)
        """

        """ Raise an exception when the number of pages in the database
            is greater or equal then 'max_pages' setting.

            Query:
            SELECT count(?) AS count_1
            FROM settings WHERE settings.name = ? AND
                 settings.value <= (SELECT count(nodes.id) AS count_2
                                   FROM nodes
                                   WHERE nodes.row_type IN (?))
        """
        n_pages = session.query(func.count(cls.id)).subquery()
        q = session.query(func.count('*')).filter(Setting.name == 'max_pages')
        q = q.filter(n_pages >= cast(Setting.raw_value, BigInteger()))

        return not bool(q.scalar())


class Section(Node):

    __mapper_args__ = {'polymorphic_identity': 'section'}

    banners = relationship('Banner', secondary=node_banners)


class ExternalLink(Node):
    __mapper_args__ = {'polymorphic_identity': 'externallink'}


class InternalLink(Node):

    __mapper_args__ = {'polymorphic_identity': 'internallink'}

    linked_to_id = Column(Integer, ForeignKey('nodes.id',
                                              onupdate='cascade',
                                              ondelete='cascade'),)
#                          nullable=False)

    linked_to = relationship('Page', backref='linked_by', remote_side=Page.id,
                            primaryjoin='Page.id == InternalLink.linked_to_id')

    @validates('linked_to')
    def validate_linked_to(self, key, value):
        #log.debug('Validate linked_to : %s, %s,%s', self, key, value)
        if not isinstance(value, (Page)):
            raise ValidationError()

        return value
