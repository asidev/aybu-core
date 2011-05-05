#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from elixir import using_options_defaults
from elixir import options_defaults

from aybu.cms.model.file import File, Image
from aybu.cms.model.types import SHA1
from aybu.cms.model.language import Language
from aybu.cms.model.setting import SettingType, Setting
from aybu.cms.model.theme import Theme
from aybu.cms.model.user import User, Group
from aybu.cms.model.view import View, ViewDescription
from aybu.cms.model.keyword import Keyword
from aybu.cms.model.graph import NodeInfo, Page,\
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
