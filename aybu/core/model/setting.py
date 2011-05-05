#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""


from elixir import Entity, Field, Unicode, String
from elixir import Boolean
from elixir import using_options
from elixir import ManyToOne, OneToMany


class SettingType(Entity):
    name = Field(Unicode(64), primary_key=True)
    settings = OneToMany("Setting")

    using_options(tablename="setting_types")

    def __str__(self):
        return "<SettingType %s>" % (self.name)

    def __repr__(self):
        return self.__str__()


class Setting(Entity):
    name = Field(Unicode(128), primary_key=True)
    value = Field(Unicode(512), required=True)
    raw_type = Field(String(8), required=True)
    ui_administrable = Field(Boolean, default=False)

    type = ManyToOne('SettingType', lazy=False,
                     onupdate="cascade", ondelete="restrict")

    using_options(tablename="settings")

    def __str__(self):
        return "<Setting %s (%s)>" % (self.name, self.raw_type)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, s):
        return self.name == s.name
