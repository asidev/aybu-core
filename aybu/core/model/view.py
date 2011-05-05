#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""


from elixir import using_table_options
from elixir import Entity, Field, Unicode, Integer, UnicodeText, String
from elixir import using_options
from elixir import ManyToOne, OneToMany
from sqlalchemy import UniqueConstraint


class View(Entity):
    id = Field(Integer, primary_key=True)
    name = Field(Unicode(255), unique=True)
    fs_view_path = Field(String(255), unique=True)

    descriptions = OneToMany("ViewDescription", cascade="all")
#    contents = OneToMany("Content")

    using_options(tablename="views")

    def __str__(self):
        return "<View %s (%s)>" % (self.name, self.fs_view_path)

    def __repr__(self):
        return self.__str__()


class ViewDescription(Entity):
    id = Field(Integer, primary_key=True)
    description = Field(UnicodeText(), default=u'')

    view = ManyToOne("View", colname="view_id",
                     onupdate='cascade', ondelete='cascade')
    lang = ManyToOne('Language', colname="lang_id",
                     onupdate='cascade', ondelete='cascade')

    using_table_options(UniqueConstraint('view_id', 'lang_id'))
    using_options(tablename="views_descriptions")

    def __str__(self):
        return "<ViewDescription %s>" % (self.description)

    def __repr__(self):
        return self.__str__()
