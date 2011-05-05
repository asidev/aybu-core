#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from elixir import using_options_defaults
from elixir import options_defaults

from aybu.core.model.file import File, Image
from aybu.core.model.types import SHA1
from aybu.core.model.language import Language
from aybu.core.model.setting import SettingType, Setting
from aybu.core.model.theme import Theme
from aybu.core.model.user import User, Group
from aybu.core.model.view import View, ViewDescription
from aybu.core.model.keyword import Keyword
from aybu.core.model.graph import NodeInfo, Page,\
                                 Section, ExternalLink, InternalLink,\
                                 Node, Menu

using_options_defaults(table_options=dict(mysql_engine="InnoDB"))
options_defaults.update(dict(table_options=dict(mysql_engine="InnoDB")))

__all__ = [
    'Language', 'Setting', 'User', 'View', 'File', 'Image', 'SHA1', 'Keyword',
    'SettingType', 'Group', 'ViewDescription', 'Keyword', 'NodeInfo',
    'Page', 'Section', 'ExternalLink', 'InternalLink', 'Node', 'Menu',
    'Theme'
]
