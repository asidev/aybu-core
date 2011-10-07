#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from aybu.core.models import Page
from aybu.core.models import Setting
from aybu.core.models import SettingType
from aybu.core.utils.exceptions import ConstraintError
from logging import getLogger
from test_base import BaseTests

log = getLogger(__name__)


class SettingTests(BaseTests):

    def test_str_and_repr(self):
        max_pages = Setting(name=u'max_pages',
                            value=u'1',
                            ui_administrable=False,
                            type=SettingType(name=u'integer',
                                             raw_type=u'int'))
        self.session.add(max_pages)
        self.assertEqual(str(max_pages), '<Setting max_pages (1)>')

    def test_get_all(self):
        max_pages = Setting(name=u'max_pages',
                            value=u'1',
                            ui_administrable=False,
                            type=SettingType(name=u'integer',
                                             raw_type=u'int'))
        self.session.add(max_pages)
        site_title = Setting(name=u'site_title',
                            value=u'Nome Sito',
                            ui_administrable=True,
                            type=SettingType(name=u'txt',
                                             raw_type=u'unicode'))
        self.session.add(site_title)
        self.session.flush()

        settings = Setting.get_all(self.session)

        for setting in (max_pages, site_title):
            self.assertIn(setting, settings)


class SettingTypeTests(BaseTests):

    def test_str_and_repr(self):
        type = SettingType(name=u'integer', raw_type=u'int')
        self.session.add(type)

        self.assertEqual(str(type), '<SettingType integer (int)>')
