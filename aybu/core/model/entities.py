#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from elixir import using_options_defaults
from elixir import options_defaults

from aybu.cms.model.entities import File, Image
from aybu.cms.model.entities import SHA1
from aybu.cms.model.entities import Language
from aybu.cms.model.entities import SettingType, Setting
from aybu.cms.model.entities import Theme
from aybu.cms.model.entities import User, Group
from aybu.cms.model.entities import View, ViewDescription
from aybu.cms.model.entities import Keyword
from aybu.cms.model.entities import NodeInfo, Page,\
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
