#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.utils.exceptions import ValidationError
from aybu.core.models.base import Base
from aybu.core.models.base import get_sliced
from aybu.core.models.view import View
from collections import deque
from logging import getLogger
from sqlalchemy import and_
from sqlalchemy import asc
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import aliased
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.sql import func


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
        return session.query(cls).get(id_)

    @classmethod
    def get_by_enabled(cls, session, enabled, start=None, limit=None):

        query = session.query(cls).filter(cls.enabled == enabled)
        return get_sliced(query, start, limit)

    @classmethod
    def get_max_weight(cls, session, **params):

        q = session.query(func.max(cls.weight))

        if 'parent' in params:
            q = q.filter(cls.parent == params['parent'])

        return  q.scalar()

    @validates('parent')
    def validate_parent(self, key, value):
        #log.debug('Validate parent : %s, %s,%s', self, key, value)
        if isinstance(self, Menu):
            if value != None:
                raise ValidationError()
        else:
            if not isinstance(value, (Menu, Section, Page)):
                raise ValidationError()

        return value

    @validates('children')
    def validate_children(self, key, value):
        #log.debug('Validate children : %s, %s,%s', self, key, value)
        if isinstance(self, (ExternalLink, InternalLink)):
            if value != None or value != []:
                raise ValidationError()
        return value

    @classmethod
    def create(cls, session, **params):
        """ Create a persistent 'cls' object and return it."""
        if cls == Node:
            raise ValidationError('cls: Node creation is not allowed!')

        entity = cls(**params)
        session.add(entity)
        return entity


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
    def get_homepage(cls, session):
        return session.query(cls).filter(cls.home == True).one()

    @classmethod
    def set_homepage(cls, session, page):
        session.query(cls).update(dict(home=False))
        session.query(cls).filter(cls.id == page.id).update(dict(home=True))

    @classmethod
    def set_default_homepage(cls, session):
        try:
            cls.get_homepage(session)
            return
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
        homepage = query.one()

        homepage.home = True

    @validates('view')
    def validate_view(self, key, value):
        if value is None:
            raise ValidationError()

        # The following control should be already checked by sqlalchemy when
        # the object is added to the session
        if not isinstance(value, View):
            raise ValidationError()

        return value

    @classmethod
    def is_last_page(cls, session):
        return True if session.query(cls).count() == 1 else False

class Section(Node):

    __mapper_args__ = {'polymorphic_identity': 'section'}

    banners = relationship('Banner', secondary=node_banners)


class ExternalLink(Node):

    __mapper_args__ = {'polymorphic_identity': 'externallink'}

    # Maybe this should be removed from here cause it can change with language
    # ie: http://www.apple.com or http://www.apple.it
    url = Column(Unicode(512), default=None)


class InternalLink(Node):

    __mapper_args__ = {'polymorphic_identity': 'internallink'}

    linked_to_id = Column(Integer, ForeignKey('nodes.id',
                                              onupdate='cascade',
                                              ondelete='cascade'),)
#                          nullable=False)

    linked_to = relationship('Page', backref='linked_by', remote_side=Page.id,
                             primaryjoin='Page.id == InternalLink.linked_to_id')
