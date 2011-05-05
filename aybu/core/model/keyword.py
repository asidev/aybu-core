#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

from elixir import Entity, Field, Unicode
from elixir import using_options
from elixir import ManyToMany

class Keyword(Entity):
    name = Field(Unicode(64), primary_key=True)
    used_in = ManyToMany("NodeInfo",
                         tablename="node_info_keywords",
                         table_kwargs=dict(useexisting=True),
                         onupdate="cascade", ondelete="cascade")

    using_options(tablename='keywords')

    def __str__(self):
        return "<Keyword %s>" % (self.name)

    def __repr__(self):
        return self.__str__()
