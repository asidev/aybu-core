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

from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm.exc import (NoResultFound,
                                MultipleResultsFound)
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.hybrid import hybrid_property
from aybu.core.models.base import Base
from aybu.core.models.node import Menu, Section, Page
from aybu.core.htmlmodifier import (update_img_src,
                                    associate_pages,
                                    associate_files,
                                    associate_images,
                                    remove_target_attributes)
from BeautifulSoup import BeautifulSoup
from sqlalchemy.orm import validates
from sqlalchemy.orm.session import object_session

__all__ = []


log = getLogger(__name__)


class NodeInfo(Base):
    __tablename__ = 'node_infos'
    __table_args__ = (UniqueConstraint('node_id', 'lang_id'),
                      {'mysql_engine': 'InnoDB'})
    discriminator = Column('row_type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}
    id = Column(Integer, primary_key=True)
    label = Column(Unicode(64), nullable=False)
    node_id = Column(Integer, ForeignKey('nodes.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)
    lang_id = Column(Integer, ForeignKey('languages.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)
    lang = relationship('Language')

    @property
    def type(self):
        return self.__class__.__name__

    def __repr__(self):
        try:
            return "<%s [%s] '%s'>" % (self.__class__.__name__, self.id,
                                       self.label.encode('utf8'))
        except:
            return super(NodeInfo, self).__repr__()

    @validates('node')
    def validate_node(self, key, value):
        if not value is None:
            self.node_id = value.id
        return value

    @classmethod
    def create_translations(cls, session, src_lang_id, dst_language):
        """ Create a translation from Language 'src_lang_id'
            to Language 'dst_language' for each NodeInfo in the database.
            NOTE: data of new translations will be data of existing ones.
        """
        translations = []

        criterion = cls.lang.has(id=src_lang_id)
        for translation in session.query(cls).filter(criterion).all():

            obj = translation.create_translation(dst_language)

            if obj not in session.new:
                session.add(obj)

            translations.append(obj)

        return translations

    @classmethod
    def remove_translations(cls, session, language_id):
        criterion = NodeInfo.lang.has(id=language_id)
        return session.query(NodeInfo).filter(criterion).delete('fetch')

    def create_translation(self, language):
        return self.__class__(label=u'{} [{}]'.format(self.label,
                                                      language.lang),
                              lang=language)

    def translate(self, enabled_only=True):

        # Avoid circular imports.
        from aybu.core.models.language import Language

        session = object_session(self)
        query = session.query(Language).filter(Language.id != self.lang.id)

        if enabled_only:
            query = query.filter(Language.enabled == True)

        for language in query.all():
            session.add(self.create_translation(language))

    def to_dict(self):
        return dict(id=self.node.id,
                    button_label=self.label,
                    enabled=self.node.enabled)


class MenuInfo(NodeInfo):
    __mapper_args__ = {'polymorphic_identity': 'menu_info'}
    node = relationship('Menu', backref='translations')

    def create_translation(self, language):
        obj = super(MenuInfo, self).create_translation(language)
        obj.node = self.node
        return obj


class CommonInfo(NodeInfo):
    __mapper_args__ = {'polymorphic_identity': 'common_info'}
    title = Column(Unicode(64), default=u'')
    url_part = Column(Unicode(64), default=u'')
    _parent_url = Column(Unicode(512), default=u'', name='parent_url')
    meta_description = Column(UnicodeText(), default=u'')
    head_content = Column(UnicodeText(), default=u'')

    @property
    def current_parent_url(self):
        # Calculate the right 'self.parent_url'.
        if isinstance(self.node.parent, (Section, Page)):
            # This CommonInfo belong to a Section|Page under Section|Page.
            # In this case the parent has 'CommonInfo.url'.
            return self.node.parent.get_translation(self.lang).url

        # This CommonInfo belong to Section|Page under a Menu.
        # 'parent_url' format must be: '/en', '/it', ...
        return '/{}'.format(self.lang.lang)

    @hybrid_property
    def parent_url(self):

        parent_url = self.current_parent_url

        if self._parent_url != parent_url:
            old_parent_url = self._parent_url
            self._parent_url = parent_url
            # Update children parent_urls before change _parent_url!
            session = object_session(self)
            criterion = CommonInfo.parent_url.ilike(str(old_parent_url) + '%')
            q = session.query(CommonInfo).filter(criterion)
            for item in q.all():
                old_item_parent_url = item._parent_url
                # Calculate a new parent_url if it is needed.
                new_item_parent_url = item.parent_url
                # Handle 'url' changes in PageInfo objects:
                # replace links in PageInfo objects that referer them.
                if isinstance(item, PageInfo):
                    log.debug('Handle child: %s', item)
                    criterion = PageInfo.links.any(PageInfo.id == item.id)
                    q = session.query(PageInfo).filter(criterion)
                    for obj in q.all():
                        log.debug('Handle links from obj: %s', obj)
                        log.debug('Obj content: %s', obj.content)
                        soup = obj.soup
                        for a in soup.findAll('a'):
                            if not a['href'].startswith(old_item_parent_url):
                                continue
                            old_href = a['href']
                            a['href'] = item.url
                            log.debug('Replaced %s with %s',
                                      old_href, a['href'])

                        # Use _content to avoid calling of hybrid_property.
                        obj._content = unicode(soup)
                        log.debug('New obj content: %s', obj.content)

        return self._parent_url

    @parent_url.setter
    def parent_url(self, value):
        # Raise an exception if 'obj.parent_url' != 'parent_url'.
        if self.parent_url != value:
            msg = "Wrong '{}.parent_url': '{}'. The right value is '{}'."
            msg = msg.format(self.__class__.__name__, value, self._parent_url)
            raise ValueError(msg)

    @parent_url.expression
    def parent_url(self):
        return self._parent_url

    @hybrid_property
    def url(self):
        # Use self.parent_url instead of self._parent_url!
        return self.parent_url + '/' + self.url_part

    def create_translation(self, language):
        obj = super(CommonInfo, self).create_translation(language)
        obj.node = self.node
        obj.title = self.title + '[{}]'.format(language.lang)
        obj.url_part = self.url_part + '[{}]'.format(language.lang)
        obj.meta_description = self.meta_description
        obj.head_content = self.head_content
        return obj

    def to_dict(self):
        dict_ = super(CommonInfo, self).to_dict()
        dict_.update(dict(title=self.title,
                          url_part=self.url_part,
                          parent_url=self.parent_url,
                          meta_description=self.meta_description,
                          head_content=self.head_content))
        return dict_


class PageInfo(CommonInfo):
    __mapper_args__ = {'polymorphic_identity': 'page_info'}
    node = relationship('Page', backref='translations')
    _content = Column(UnicodeText(), default=u'', name='content')

    _files_table = Table('node_infos_files__files',
                         Base.metadata,
                         Column('node_infos_id',
                                Integer,
                                ForeignKey('node_infos.id',
                                           onupdate="cascade",
                                           ondelete="cascade")),
                         Column('files_id',
                                Integer,
                                ForeignKey('files.id',
                                           onupdate="cascade",
                                           ondelete="cascade")))
    files = relationship('File', secondary=_files_table)

    _images_table = Table('node_infos_images__files',
                          Base.metadata,
                          Column('node_infos_id',
                                 Integer,
                                 ForeignKey('node_infos.id',
                                            onupdate="cascade",
                                            ondelete="cascade")),
                          Column('files_id',
                                 Integer,
                                 ForeignKey('files.id',
                                            onupdate="cascade",
                                            ondelete="cascade")))
    images = relationship('Image', secondary=_images_table)

    _links_table = Table('node_infos_links__node_infos',
                         Base.metadata,
                         Column('inverse_id',
                                Integer,
                                ForeignKey('node_infos.id',
                                           onupdate="cascade",
                                           ondelete="cascade")),
                         Column('links_id',
                                Integer,
                                ForeignKey('node_infos.id',
                                           onupdate="cascade",
                                           ondelete="cascade")))
    links = relationship('PageInfo', secondary=_links_table,
                         primaryjoin=NodeInfo.id == _links_table.c.inverse_id,
                         secondaryjoin=NodeInfo.id == _links_table.c.links_id)

    def __repr__(self):
        try:
            url = '' if self.url is None else self.url
            return "<PageInfo [%s] '%s' %s>" % (self.id,
                                                self.label.encode('utf8'),
                                                url.encode('utf8'))
        except:
            return super(PageInfo, self).__repr__()

    @hybrid_property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        soup = BeautifulSoup(value, smartQuotesTo=None)
        soup = associate_images(soup, self)
        soup = associate_files(soup, self)
        soup = associate_pages(soup, self)
        soup = remove_target_attributes(soup)
        self._content = unicode(soup)

    def create_translation(self, language):
        obj = super(PageInfo, self).create_translation(language)
        obj.content = self.content
        obj.node = self.node
        obj.files.extend([file_ for file_ in self.files])
        obj.images.extend([image for image in self.images])
        obj.links.extend([link for link in self.links])
        return obj

    @classmethod
    def get_by_url(cls, session, url):
        criterion = cls.url.ilike(url)
        return session.query(cls).filter(criterion).one()

    @classmethod
    def get_homepage(cls, session, language):
        page = Page.get_homepage(session)
        query = session.query(cls).filter(cls.node == page)\
                                  .filter(cls.lang == language)
        return query.one()

    @property
    def soup(self):
        return BeautifulSoup(self.content, smartQuotesTo=None)

    def update_image_src(self, image):
        self.content = unicode(update_img_src(self.soup, image))
        return self.soup

    def to_dict(self):
        dict_ = super(PageInfo, self).to_dict()
        dict_.update(dict(page_type_id=self.node.view.id))
        return dict_

class SectionInfo(CommonInfo):
    __mapper_args__ = {'polymorphic_identity': 'section_info'}
    node = relationship('Section', backref='translations')

    def create_translation(self, language):
        obj = super(SectionInfo, self).create_translation(language)
        obj.node = self.node
        return obj


class ExternalLinkInfo(NodeInfo):
    __mapper_args__ = {'polymorphic_identity': 'externallink_info'}
    node = relationship('ExternalLink', backref='translations')
    # This is has been moved from ExternalLink to internationalize the
    # external link too
    # ie: http://www.apple.com or http://www.apple.it
    ext_url = Column(Unicode(512), default=None)

    def create_translation(self, language):
        obj = super(ExternalLinkInfo, self).create_translation(language)
        obj.ext_url = self.ext_url
        obj.node = self.node
        return obj

    def to_dict(self):
        dict_ = super(ExternalLinkInfo, self).to_dict()
        dict_.update(dict(external_url=self.node.url))
        return dict_


class InternalLinkInfo(NodeInfo):
    __mapper_args__ = {'polymorphic_identity': 'internallink_info'}
    node = relationship('InternalLink', backref='translations')

    def create_translation(self, language):
        obj = super(InternalLinkInfo, self).create_translation(language)
        obj.node = self.node
        return obj

    def to_dict(self):
        dict_ = super(ExternalLinkInfo, self).to_dict()
        dict_.update(dict(linked_to=self.node.linked_to.id))
        return dict_
