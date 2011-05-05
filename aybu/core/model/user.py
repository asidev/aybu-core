#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from elixir import Entity, Field, Unicode
from elixir import using_options
from elixir import ManyToMany
from aybu.core.model.types import SHA1


class User(Entity):
    username = Field(Unicode(255), primary_key=True)
    password = Field(SHA1(), required=True)
    groups = ManyToMany('Group', tablename="users_groups")

    using_options(tablename="users")

    def is_admin(self):
        if "admin" in (g.name for g in self.groups):
            return True
        return False

    def __str__(self):
        return "<User %s>" % (self.username)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.username == other.username


class Group(Entity):
    name = Field(Unicode(32), primary_key=True)
    users = ManyToMany('User', tablename="users_groups")

    using_options(tablename="groups")

    def __str__(self):
        return "<Group {0}>".format(self.name)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name
