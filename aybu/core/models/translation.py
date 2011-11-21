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
from sqlalchemy.util.langhelpers import symbol
from aybu.core.models.base import Base
from aybu.core.models.node import Menu, Section, Page
from aybu.core.htmlmodifier import (update_img_src,
                                    associate_pages,
                                    associate_files,
                                    associate_images,
                                    remove_target_attributes)
from BeautifulSoup import BeautifulSoup

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
    parent_url = Column(Unicode(512), default=u'')
    meta_description = Column(UnicodeText(), default=u'')
    head_content = Column(UnicodeText(), default=u'')

    @hybrid_property
    def url(self):
        # Use as is!!! Don't use str.format or '%s/%s' % (...)
        # Filtering will not work!
        return self.parent_url + '/' + self.url_part

    @url.setter
    def url(self, url):
        """ Split value into 'parent_url' and 'url_part' parts.

            For example, '/en/company/about_us.html' will be split into
            '/en/company' (parent_url) and 'about_us' (url_part).
        """
        self.parent_url, self.url_part = url.rsplit('.', 1)[0].rsplit('/', 1)

    @classmethod
    def on_attr_update(cls, obj, new, old, attr):
        if not hasattr(obj, '_attrs_updates'):
            obj._attrs_updates = {}
        obj._attrs_updates[attr.key] = dict(old=old, new=new)
        return new

    @classmethod
    def after_flush(cls, session, *args):
        """ Set 'parent_url' and update it when 'url_part' was changed.
        """

        log.debug('Executing after_flush on CommonInfo.')

        for obj in session:

            if not isinstance(obj, CommonInfo) or \
               not hasattr(obj, '_attrs_updates'):
                continue

            log.debug('Handle obj: %s', obj)

            if 'url_part' in obj._attrs_updates and \
               obj._attrs_updates['url_part']['old'] != symbol('NO_VALUE') and \
               obj._attrs_updates['url_part']['old'] != symbol('NEVER_SET') and \
               obj.node.children:

                old = '{}/{}'.format(obj.parent_url,
                                     obj._attrs_updates['url_part']['old'])
                new = '{}/{}'.format(obj.parent_url,
                                     obj._attrs_updates['url_part']['new'])

                # Update children.
                criterion = cls.parent_url.ilike(old + '%')
                for item in session.query(cls).filter(criterion).all():
                    item.parent_url = item.parent_url.replace(old, new, 1)

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
    content = Column(UnicodeText(), default=u'')

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

    def create_translation(self, language):
        obj = super(PageInfo, self).create_translation(language)
        obj.url = self.url
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

    @classmethod
    def before_flush(cls, session, flush_context, instances):
        """ When updating content, parse and update relations """
        log.debug("Executing before_flush on PageInfo")
        pages = [obj for obj in session.new if type(obj) == cls and obj.content]
        pages.extend([obj for obj in session.dirty if type(obj) == cls and
                      obj.content])
        log.debug("Instances: %s", pages)
        for instance in pages:
            log.debug("instance.content: %s", instance.content)
            soup = BeautifulSoup(instance.content, smartQuotesTo=None)
            soup = associate_images(soup, instance)
            soup = associate_files(soup, instance)
            soup = associate_pages(soup, instance)
            soup = remove_target_attributes(soup)
            instance.content = unicode(soup)

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
