#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.sql import func

from aybu.website.models.base import Base
from aybu.website.models.base import get_sliced
from aybu.website.models.language import Language


__all__ = []


log = getLogger(__name__)


class NodeInfo(Base):

    __tablename__ = 'node_infos'

    id = Column(Integer, primary_key=True)
    label = Column(Unicode(64), nullable=False)
    title = Column(Unicode(64), default=None)
    url_part = Column(Unicode(64), default=None)

    # This field is very useful but denormalize the DB
    url = Column(Unicode(512), default=None)

    node_id = Column(Integer, ForeignKey('nodes.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)

    node = relationship('Node', backref='translations')

    lang_id = Column(Integer, ForeignKey('languages.id',
                                         onupdate='cascade',
                                         ondelete='cascade'), nullable=False)

    lang = relationship('Language')

    meta_description = Column(UnicodeText(), default=u'')
    head_content = Column(UnicodeText(), default=u'')
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
    links = relationship('NodeInfo', secondary=_links_table,
                         primaryjoin=id==_links_table.c.inverse_id,
                         secondaryjoin=id==_links_table.c.links_id)

    def __repr__(self):
        url = '' if self.url is None else self.url

        return "<NodeInfo [%d] '%s' %s>" % (self.id,
                                            self.label.encode('utf8'),
                                            url.encode('utf8'))

    @classmethod
    def get_by_url(cls, session, url):
        criterion = cls.url.ilike(url)
        return session.query(cls).filter(criterion).one()

    @classmethod
    def get_homepage(cls, session, language=None):

        # Get the NodeInfo which belongs to the 'home' Node.
        query = session.query(cls).filter(cls.node.has(Page.home == True))

        if not language is None:
            query = query.filter(cls.lang == language)

        try:
            return query.one()
        except NoResultFound as e:
            log.debug(e)

        # There is no node with home == True.
        # Get the NodeInfo of the Page with min weight in the main Menu.
        query = session.query(func.min(Page.weight).label('min_weight'))
        criterion = Page.parent.has(and_(Menu.weight == 1,
                                         Menu.parent == None))
        query = query.filter(criterion).group_by(Page.weight)
        criterion = and_(Page.parent.has(and_(Menu.weight == 1,
                                              Menu.parent == None)),
                         Page.weight == query.subquery())
        query = session.query(Page).filter(criterion)
        page = aliased(Page, query.subquery())
        query = session.query(cls).filter(cls.lang == language)
        query = query.join(page, cls.node)

        home = query.first()
        if home is None:
            # The previous query is empty.
            # Get the NodeInfo of the first inserted Page.
            query = session.query(cls).filter(cls.lang == language)
            query = query.join(Page).order_by(asc(Page.id))
            home = query.first()

        if not home is None:
            home.node.home = True
            session.commit()

        return home
