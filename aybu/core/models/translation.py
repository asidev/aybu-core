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
from sqlalchemy.orm import backref
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
    lang = relationship('Language', lazy='joined')

    @property
    def type(self):
        return self.__class__.__name__

    def __repr__(self):
        try:
            return "<%s [%s] '%s'>" % (self.__class__.__name__, self.id,
                                       self.label.encode('utf8'))
        except:
            return super(NodeInfo, self).__repr__()

    @classmethod
    def create_translations(cls, session, src_lang_id, dst_language):
        """ Create a translation from Language 'src_lang_id'
            to Language 'dst_language' for each NodeInfo in the database.
            NOTE: data of new translations will be data of existing ones.
        """
        translations = []

        criterion = cls.lang.has(id=src_lang_id)
        for translation in session.query(cls).filter(criterion).all():

            obj = translation.create_translation(language=dst_language)

            if obj not in session.new:
                session.add(obj)

            translations.append(obj)

        return translations

    @classmethod
    def remove_translations(cls, session, language_id):
        criterion = NodeInfo.lang.has(id=language_id)
        return session.query(NodeInfo).filter(criterion).delete('fetch')

    def create_translation(self, language, **kwargs):
        kwargs['label'] = u'{} [{}]'.format(self.label, language.lang)
        kwargs['lang'] = language
        return self.__class__(**kwargs)

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
    node = relationship('Menu',
                        backref=backref('translations', lazy='joined'),
                        lazy='joined')

    def create_translation(self, **kwargs):
        kwargs['node'] = self.node
        return super(MenuInfo, self).create_translation(**kwargs)


class CommonInfo(NodeInfo):
    __mapper_args__ = {'polymorphic_identity': 'common_info'}
    title = Column(Unicode(64), default=u'')
    url_part = Column(Unicode(64), default=u'')
    _parent_url = Column(Unicode(512), default=u'', name='parent_url')
    meta_description = Column(UnicodeText(), default=u'')
    head_content = Column(UnicodeText(), default=u'')

    @hybrid_property
    def parent_url(self):
        # Calculate 'parent_url'.
        if isinstance(self.node.parent, (Section, Page)):
            # This CommonInfo belong to a Section|Page under Section|Page.
            # In this case the parent has 'CommonInfo.url'.
            parent_url = self.node.parent.get_translation(self.lang).url

        else:
            # This CommonInfo belong to Section|Page under a Menu.
            # 'parent_url' format must be: '/en', '/it', ...
            parent_url = '/{}'.format(self.lang.lang)
        return parent_url

    @parent_url.expression
    def parent_url(self):
        return self._parent_url

    @hybrid_property
    def url(self):
        # Use self.parent_url instead of self._parent_url!
        return self.parent_url + '/' + self.url_part

    def update_parent_url(self):

        parent_url = self.parent_url

        if self._parent_url != parent_url:

            log.debug("Updating 'parent_url' of %s from %s to %s",
                      self.label, self._parent_url, parent_url)

            old_url = '{}/{}'.format(self._parent_url, self.url_part)
            self._parent_url = parent_url
            new_url = self.url
            log.debug('URL is %s.', new_url)

            self.update_children_parent_url()

            if isinstance(self, PageInfo):
                for obj in self.referers:
                    soup = obj.soup
                    for a in soup.findAll('a'):
                        if a['href'] == old_url:
                            log.debug('Found %s in %s', obj.label, old_url)
                            a['href'] = new_url
                    # Use _content to avoid calling of hybrid_property.
                    obj.content = unicode(soup)

        return self._parent_url

    def update_children_parent_url(self):
        # Trigger the change of 'parent_url' to the children.
        log.debug('Triggering change event to children ...')
        for obj in self.node.children:

            if not isinstance(obj, (Section, Page)):
                continue

            log.debug('Handle translations of %s.', obj.id)

            for translation in obj.translations:

                if translation.lang != self.lang:
                    continue

                log.debug('Handle translation %s.', translation.label)
                translation.update_parent_url()

    def create_translation(self, **kwargs):
        kwargs['title'] = self.title + '[{}]'.format(kwargs['language'].lang)
        kwargs['url_part'] = self.url_part + '[{}]'.format(kwargs['language'].lang)
        kwargs['meta_description'] = self.meta_description
        kwargs['head_content'] = self.head_content
        return super(CommonInfo, self).create_translation(**kwargs)

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
    node = relationship('Page',
                        backref=backref('translations', lazy='joined'),
                        lazy='joined')
    content = Column(UnicodeText(), default=u'', name='content')

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
                         secondaryjoin=NodeInfo.id == _links_table.c.links_id,
                         backref=backref('referers', lazy='joined'),
                         lazy='joined')

    def __repr__(self):
        try:
            url = '' if self.url is None else self.url
            return "<PageInfo [%s] '%s' %s>" % (self.id,
                                                self.label.encode('utf8'),
                                                url.encode('utf8'))
        except:
            return super(PageInfo, self).__repr__()

    @property
    def soup(self):
        return BeautifulSoup(self.content, smartQuotesTo=None)

    def update_associations(self):
        """ Parse content and fill relationships: files, images, links.
        """
        soup = self.soup
        soup = associate_images(soup, self)
        soup = associate_files(soup, self)
        soup = associate_pages(soup, self)
        soup = remove_target_attributes(soup)
        self.content = unicode(soup)

    def create_translation(self, **kwargs):
        kwargs['content'] = self.content
        kwargs['node'] = self.node
        kwargs['files'] = [file_ for file_ in self.files]
        kwargs['images'] = [image for image in self.images]
        kwargs['links'] = [link for link in self.links]
        return super(PageInfo, self).create_translation(**kwargs)

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

    def update_image_src(self, image):
        self.content = unicode(update_img_src(self.soup, image))
        return self.soup

    def to_dict(self):
        dict_ = super(PageInfo, self).to_dict()
        dict_.update(dict(page_type_id=self.node.view.id))
        return dict_


class SectionInfo(CommonInfo):
    __mapper_args__ = {'polymorphic_identity': 'section_info'}
    node = relationship('Section',
                        backref=backref('translations', lazy='joined'),
                        lazy='joined')

    def create_translation(self, **kwargs):
        kwargs['node'] = self.node
        return super(SectionInfo, self).create_translation(**kwargs)


class ExternalLinkInfo(NodeInfo):
    __mapper_args__ = {'polymorphic_identity': 'externallink_info'}
    node = relationship('ExternalLink',
                        backref=backref('translations', lazy='joined'),
                        lazy='joined')
    # This is has been moved from ExternalLink to internationalize the
    # external link too
    # ie: http://www.apple.com or http://www.apple.it
    ext_url = Column(Unicode(512), default=None)

    def create_translation(self, **kwargs):
        kwargs['ext_url'] = self.ext_url
        kwargs['node'] = self.node
        return super(ExternalLinkInfo, self).create_translation(**kwargs)

    def to_dict(self):
        dict_ = super(ExternalLinkInfo, self).to_dict()
        dict_.update(dict(external_url=self.node.url))
        return dict_


class InternalLinkInfo(NodeInfo):
    __mapper_args__ = {'polymorphic_identity': 'internallink_info'}
    node = relationship('InternalLink',
                        backref=backref('translations', lazy='joined'),
                        lazy='joined')

    def create_translation(self, **kwargs):
        kwargs['node'] = self.node
        return super(InternalLinkInfo, self).create_translation(**kwargs)

    def to_dict(self):
        dict_ = super(ExternalLinkInfo, self).to_dict()
        dict_.update(dict(linked_to=self.node.linked_to.id))
        return dict_
