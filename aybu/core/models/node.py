#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models.base import Base
from aybu.core.models.base import get_sliced
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

    def __str__(self):
        return "<Node (%s) [id: %d, parent: %s, weigth:%d]>" % \
                (self.__class__.__name__, self.id, self.parent_id, self.weight)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def get_by_id(cls, session, id_):
        return session.query(cls).get(id_)

    @classmethod
    def get_by_enabled(cls, session, enabled=None, start=None, limit=None):

        query = session.query(cls)

        if not enabled is None:
            query = query.filter(cls.enabled == enabled)

        return get_sliced(query, start, limit)

    @classmethod
    def get_max_weight(cls, session, parent=None):

        q = session.query(func.max(cls.weight))

        if not parent is None:
            q = q.filter(cls.parent == parent)

        return  q.group_by(cls.weight).scalar()

    @validates('parent')
    def validate_parent(self, key, value):
        print "parent Validator."
        return value

    @validates('parent_id')
    def validate_parent_id(self, key, value):
        print "parent_id validator."
        return value

    @validates('children')
    def validate_children(self, key, value):
        print "Children validator."
        return value


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
    sitemap_priority = Column(Integer, default=50, nullable=False)
    banners = relationship('Banner', secondary=node_banners)

    view_id = Column(Integer, ForeignKey('views.id',
                                         onupdate='cascade',
                                         ondelete='restrict'), nullable=False)
    view = relationship('View')

    @classmethod
    def set_homepage(cls, session, page):
        # Get the old home and set the attribute home to False

        # Set the page passed as argument to home setting it's own attribute
        # home to True
        pass

    @classmethod
    def check_page_limit(cls, session):
        q = session.query(Setting)
        max_pages_setting = q.filter(Setting.name=='max_pages').one()
        max_pages = max_pages_setting.value

        if max_pages <= 0:
            log.debug('No limit to pages can be created')
            return True

        log.debug('The maximun number of pages can be created is %d' % count)

        num_pages = session.query(Page).count()
        log.debug('The total number of pages is %d' % num_pages)

        if max_pages <= num_pages:
            return False

        return True


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
