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
from aybu.core.exc import ValidationError, ConstraintError
from aybu.core.models.base import Base
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
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.schema import Sequence


__all__ = []
log = getLogger(__name__)


class Node(Base):

    __tablename__ = 'nodes'
    __table_args__ = (UniqueConstraint('parent_id', 'weight'),
                      {'mysql_engine': 'InnoDB'})
    discriminator = Column('row_type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    id_seq = Sequence("{}_id_seq".format(__tablename__))
    id = Column(Integer, id_seq, primary_key=True)
    enabled = Column(Boolean, default=True)
    hidden = Column(Boolean, default=False)
    weight = Column(Integer, nullable=False)

    parent_id = Column(Integer, ForeignKey('nodes.id'))
    children = relationship('Node',
                            backref=backref('parent',
                                            lazy='immediate',
                                            join_depth=5,
                                            remote_side=[id]),
                            primaryjoin='Node.id == Node.parent_id',
                            lazy='immediate',
                            join_depth=5,
                            order_by=weight)

    @property
    def type(self):
        return self.__class__.__name__

    def __repr__(self):
        try:
            parent_id = None if self.parent is None else self.parent.id
            return '<%s id="%s" parent="%s" weight="%s" />' % (self.type,
                                                               self.id,
                                                               parent_id,
                                                               self.weight)
        except:
            return '<%s>' % (self.type)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def all(cls, session, start=None, limit=None):
        # query_options must not be in the method signature:
        # the user should not use SQLA internals.
        query_options = [joinedload('parent'), joinedload('children')]
        if hasattr(cls, 'translations'):
            query_options.append(joinedload('translations'))
        return super(Node, cls).all(session, start=start, limit=limit,
                                    query_options=query_options)

    @classmethod
    def get_by_id(cls, session, id_):
        return cls.get(session, id_)

    @classmethod
    def get_by_enabled(cls, session, enabled, start=None, limit=None):
        return cls.search(session, filters=(cls.enabled == enabled,),
                          start=start, limit=limit)

    @classmethod
    def get_max_weight(cls, session, parent):
        value = session.query(func.max(cls.weight))\
                       .filter(cls.parent == parent).scalar()
        if not value:
            value = 0
        return value

    @classmethod
    def delete(cls, session, id_):
        """ Delete (and all its translations) a node from the database.
        """
        node = Node.get(session, id_)

        if isinstance(node, Menu):
            raise ConstraintError('Menu deletion is not allowed.')

        if isinstance(node, Page) and \
           Page.count(session, Page.enabled == True) < 2:
            raise ConstraintError('Last Page cannot be deleted.')

        if node.children:
            # This constraint simplify node deletion:
            # update of children (weight, parent and urls) is not needed.
            raise ConstraintError('Cannot delete a Node with children.')

        if isinstance(node, Page):
            # FIXME: add constraint!
            # Cannot delete a PageInfo when it is referred by other PageInfo.
            from aybu.core.models.translation import PageInfo
            for page_info in node.translations:

                if PageInfo.count(session,
                                  PageInfo.links.contains(page_info)):
                    raise ConstraintError('Cannot delete a referred Page.')

                # FIXME: test Pufferfish to verify files deletion.
                page_info.delete()

        session.delete(node)

    @classmethod
    def move(cls, session, id_, parent_id, previous_node_id):
        """ Move a node from position to another in the Node tree.
        """
        node = Node.get(session, id_)
        parent = Node.get(session, parent_id)

        if isinstance(node, Menu):
            raise ConstraintError('Menu cannot be moved.')

        if not isinstance(parent, (Menu, Page, Section)):
            msg = '%s cannot have children.' % parent.__class__.__name__
            raise ConstraintError(msg)

        if not previous_node_id is None:
            previous = Node.get(session, previous_node_id)
        else:
            previous = None

        q = session.query(Node).filter(Node.parent == parent)

        if previous is None:
            weight = 1
            q = q.filter(Node.weight >= 0)

        else:
            weight = previous.weight + 1
            q = q.filter(Node.weight > previous.weight)

        q.update({'weight': Node.weight + 1})
        session.flush()
        node.weight = weight
        node.parent = parent

    @validates('parent')
    def validate_parent(self, key, value):

        if isinstance(self, Menu) and not value is None:
            raise ValidationError('Menus cannot have any parent.')

        elif not isinstance(self, Menu) and\
             not isinstance(value, (Menu, Section, Page)):

            msg = '%s: parent=%s is not allowed.' % (self, value)
            raise ValidationError(msg)

        if not value is None:
            self.parent_id = value.id

        return value

    @validates('children')
    def validate_children(self, key, value):
        #FIXME: check usage!
        if isinstance(self, (ExternalLink, InternalLink)):
            if value != None or value != []:
                raise ValidationError('children')
        return value

    def get_translation(self, language):

        for translation in self.translations:
            if translation.lang == language:
                return translation

        raise NoResultFound('No translation for %s.' % language.lang)

    def to_dict(self, language=None, recursive=True):
        # Import statement to avoid circular imports.
        from aybu.core.models.media import MediaItemPage
        return dict(id=self.id,
                    type=self.type,
                    iconCls=self.type,
                    enabled=self.enabled,
                    hidden=self.hidden,
                    weight=self.weight,
                    checked=False,
                    allowChildren=True,
                    leaf=False if self.children else True,
                    expanded=True if self.children else False,
                    children=[child.to_dict(language, recursive)
                              for child in self.children
                              if recursive \
                                and not isinstance(child, MediaItemPage)])


class Menu(Node):

    __mapper_args__ = {'polymorphic_identity': 'menu'}

    def to_dict(self, language=None, recursive=True):
        dict_ = super(Menu, self).to_dict(language, recursive)
        dict_['iconCls'] = 'folder'

        for translation in self.translations:
            if translation.lang == language:
                dict_['button_label'] = translation.label

        return dict_


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
            raise ValidationError('view: cannot be None.')

        # The following control should be already checked by sqlalchemy when
        # the object is added to the session
        if not isinstance(value, View):
            raise ValidationError('view: is not a View instance.')

        return value

    @validates('sitemap_priority')
    def validate_sitemap_priority(self, key, value):
        if value > 100 or value < 1:
            # CHECK
            # We can set the default value or raise the exception
            raise ValidationError('sitemap_priority: wrong value.')
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

    def to_dict(self, language=None, recursive=True):

        dict_ = super(Page, self).to_dict(language, recursive)
        dict_['home'] = self.home

        for translation in self.translations:
            if translation.lang == language:
                dict_['button_label'] = translation.label
                dict_['url'] = translation.url
                dict_['title'] = translation.title

        return dict_


class Section(Node):
    __mapper_args__ = {'polymorphic_identity': 'section'}

    def to_dict(self, language=None, recursive=True):

        dict_ = super(Section, self).to_dict(language, recursive)

        for translation in self.translations:
            if translation.lang == language:
                dict_['button_label'] = translation.label
                dict_['title'] = translation.title

        return dict_


class ExternalLink(Node):
    __mapper_args__ = {'polymorphic_identity': 'externallink'}

    def to_dict(self, language=None, recursive=True):

        dict_ = super(ExternalLink, self).to_dict(language, recursive)
        dict_['allowChildren'] = False

        for translation in self.translations:
            if translation.lang == language:
                dict_['button_label'] = translation.label
                dict_['url'] = translation.ext_url

        return dict_


class InternalLink(Node):
    __mapper_args__ = {'polymorphic_identity': 'internallink'}
    linked_to_id = Column(Integer, ForeignKey('nodes.id',
                                              onupdate='cascade',
                                              ondelete='cascade'),)

    linked_to = relationship(
            'Page',
            backref=backref('linked_by', lazy='joined'),
            remote_side=Page.id,
            primaryjoin='Page.id == InternalLink.linked_to_id',
            lazy='joined'
    )

    @validates('linked_to')
    def validate_linked_to(self, key, value):
        #log.debug('Validate linked_to : %s, %s,%s', self, key, value)
        if not isinstance(value, (Page)):
            raise ValidationError('linked_to: is not a Page instance.')

        return value

    def to_dict(self, language=None, recursive=True):

        dict_ = super(InternalLink, self).to_dict(language, recursive)
        dict_['allowChildren'] = False

        for translation in self.translations:
            if translation.lang == language:
                dict_['button_label'] = translation.label

        for translation in self.linked_to.translations:
            if translation.lang == language:
                dict_['url'] = translation.url

        return dict_
