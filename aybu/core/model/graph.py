#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

from elixir import using_table_options
from elixir import Entity, Field, Unicode, Integer, UnicodeText
from elixir import Boolean
from elixir import using_options
from elixir import ManyToOne, OneToMany, ManyToMany
from sqlalchemy import UniqueConstraint
from aybu.core.model.entities import Language
from collections import deque

import logging
log = logging.getLogger(__name__)


class Node(Entity):
    id = Field(Integer, primary_key=True)
    enabled = Field(Boolean, default=True)
    weight = Field(Integer)

    children = OneToMany('Node', inverse="parent", order_by='weight')
    parent = ManyToOne('Node', colname="parent_id")
    translations = OneToMany('NodeInfo')
    sitemap_priority = Field(Integer, default=50)

    using_table_options(UniqueConstraint('parent_id', 'weight'))
    using_options(tablename='nodes')

    @classmethod
    def root(cls, weight=1):
        return Menu.query.filter(Menu.weight == weight).one()

    def __getitem__(self, lang):
        if isinstance(lang, Language):
            try:
                return NodeInfo.query.filter(NodeInfo.node == self).\
                                      filter(NodeInfo.lang == lang).one()
            except Exception as e:
                log.exception(e)

        raise KeyError(lang)

    @property
    def linked_by(self):
        return Node.query.filter(InternalLink.linked_to == self).all()

    @property
    def pages(self):
        return [p for p in self.crawl() if isinstance(p, Page)]

    def crawl(self, callback=None):
        queue = deque([self])
        visited = deque()
        while queue:
            parent = queue.popleft()
            if parent in visited:
                continue
            yield parent
            if callback:
                callback(parent)
            visited.append(parent)
            queue.extend(parent.children)

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def path(self):
        """ Get all parents paths as a list
            i.e. with the tree A --> B --> C get_parents_path(C) returns [A, B]
        """
        n = self
        path = [self]
        while n.parent:
            n = n.parent
            path.insert(0, n)
        return path

    def __str__(self):
        return "<Node (%s) [id: %d, parent: %s, weigth:%d]>" % \
                (self.type, self.id, self.parent_id, self.weight)

    def __repr__(self):
        return self.__str__()


class NodeInfo(Entity):
    id = Field(Integer, primary_key=True)
    label = Field(Unicode(64), required=True)
    title = Field(Unicode(64), default=None)
    url_part = Field(Unicode(64))
    node = ManyToOne('Node', onupdate='cascade', ondelete='cascade',
                         colname='node_id')
    lang = ManyToOne("Language", colname="lang_id",
                     onupdate='cascade', ondelete='cascade')

    keywords = ManyToMany("Keyword",
                          tablename="node_info_keywords",
                          table_kwargs=dict(useexisting=True),
                          onupdate="cascade", ondelete="cascade")
    meta_description = Field(UnicodeText(), default=u'')

    head_content = Field(UnicodeText(), default=u'')
    content = Field(UnicodeText(), default=u'')
    files = ManyToMany('File')
    images = ManyToMany('Image')
    links = ManyToMany('Node')
    using_options(tablename='pages')

    @property
    def url(self):
        if type(self.node) == Page:
            _url = "/{0}".format(self.lang.lang)
            for node in self.node.path[1:]:
                _url = "{0}/{1}".format(_url, node[self.lang].url_part)
            # FIXME: append ?admin if user is logged and is not reloading
            _url = _url + ".html"
            return _url
        if type(self.node) in (Menu, Section):
            return None
        if type(self.node) == (InternalLink):
            return self.node.linked_to[self.lang].url
        if type(self.node) == (ExternalLink):
            return self.node.url

    def __str__(self):
        return "<NodeInfo [%d] '%s' %s>" % (self.id, self.label, self.url)

    def __repr__(self):
        return self.__str__()


class Menu(Node):
    using_options(inheritance='single')


class Page(Node):
    view = ManyToOne("View", onupdate='cascade', ondelete='restrict')
    using_options(inheritance='single')


class Section(Node):
    using_options(inheritance='single')


class ExternalLink(Node):
    url = Field(Unicode(512), default=None)
    using_options(inheritance='single')


class InternalLink(Node):
    linked_to = ManyToOne("Node", colname="linked_to_id",
                          ondelete="cascade", onupdate="cascade")
    using_options(inheritance='single')
