#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from elixir import Entity, Field, Unicode
from elixir import using_options
from elixir import ManyToOne, OneToMany

from makako.containers import Storage


class Theme(Entity):
    name = Field(Unicode(128), primary_key=True)
    children = OneToMany('Theme')
    # set cascade to "save-update" (the default is "save-update, merge", thus
    # disabling the merge cascade which saves us one query while merging theme
    # back from cache. Parent will be lazy loaded on access.
    parent = ManyToOne('Theme', colname="parent_name", cascade="save-update",
                       lazy=False)

    using_options(tablename='theme')

    def __str__(self):
        return "<Theme '%s'>" % (self.name)

    def __repr__(self):
        return "<Theme '%s' (parent: %s)>" % (self.name, self.parent.name)

    def to_storage(self, children=True):
        s = Storage(self.to_dict())
        s.parent = self.parent.\
                   to_storage(children=False) if self.parent else None
        if children:
                s.children = [c.to_storage() for c in self.children]
        return s
