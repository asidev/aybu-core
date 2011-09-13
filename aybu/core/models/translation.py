#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import aliased
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from aybu.core.models.base import Base
from aybu.core.models.node import Page
from aybu.core.utils.exceptions import ValidationError

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
    #node = relationship('Node', backref='translations')

    lang_id = Column(Integer, ForeignKey('languages.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)
    lang = relationship('Language')

    def __repr__(self):
        return "<%s [%d] '%s'>" % (self.__class__.__name__, self.id,
                                   self.label.encode('utf8'))

    @classmethod
    def create(cls, session, **params):
        """ Create a persistent 'cls' object and return it."""
        if cls == NodeInfo:
            raise ValidationError('cls: NodeInfo creation is not allowed!')

        entity = cls(**params)
        session.add(entity)
        return entity

class CommonInfo(NodeInfo):

    #__mapper_args__ = {'polymorphic_identity': 'common_info'}

    title = Column(Unicode(64), default=None)
    url_part = Column(Unicode(64), default=None)

    # This field is very useful but denormalize the DB
    partial_url = Column(Unicode(512), default=None)

    meta_description = Column(UnicodeText(), default=u'')
    head_content = Column(UnicodeText(), default=u'')


class PageInfo(CommonInfo):

    __mapper_args__ = {'polymorphic_identity': 'page_info'}

    # This field is very useful but denormalize the DB
    url = Column(Unicode(512), default=None)

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
                         primaryjoin=NodeInfo.id==_links_table.c.inverse_id,
                         secondaryjoin=NodeInfo.id==_links_table.c.links_id)

    def __repr__(self):
        url = '' if self.url is None else self.url

        return "<PageInfo [%d] '%s' %s>" % (self.id,
                                            self.label.encode('utf8'),
                                            url.encode('utf8'))

    @classmethod
    def get_by_url(cls, session, url):
        criterion = cls.url.ilike(url)
        return session.query(cls).filter(criterion).one()

    @classmethod
    def get_homepage(cls, session, language):

        try:
            Page.get_homepage(session)
        except (MultipleResultsFound, NoResultFound):
            Page.set_default_homepage(session)

        query = session.query(Page).filter(Page.home==True)
        page = aliased(Page, query.subquery())
        query = session.query(cls).filter(cls.lang == language)
        query = query.join(page, cls.node)
        return query.one()


class SectionInfo(CommonInfo):

    __mapper_args__ = {'polymorphic_identity': 'section_info'}

    node = relationship('Section', backref='translations')


class ExternalLinkInfo(NodeInfo):

    __mapper_args__ = {'polymorphic_identity': 'externallink_info'}

    node = relationship('ExternalLink', backref='translations')


class InternalLinkInfo(NodeInfo):

    __mapper_args__ = {'polymorphic_identity': 'internallink_info'}

    node = relationship('InternalLink', backref='translations')
