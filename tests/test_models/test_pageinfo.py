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

import ConfigParser
import StringIO

from aybu.core.models import Node, NodeInfo, Menu, MenuInfo, Page, PageInfo
from aybu.core.models import Section, SectionInfo
from aybu.core.models import ExternalLinkInfo
from aybu.core.models import InternalLinkInfo
from aybu.core.models import Language
from aybu.core.models import default_data_from_config
from aybu.core.models import populate
from logging import getLogger
from test_base import BaseTests

from sqlalchemy.sql import func

log = getLogger(__name__)


class PageInfoTests(BaseTests):

    def create_pageinfo(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page = Page(id=2, parent=menu, weight=1)
        self.session.add(page)
        lang = Language(lang=u'it', country=u'it')
        self.session.add(lang)

        page_info = PageInfo(id=1, label='Home', title='Pagina Principale',
                             url_part='index', node=page, lang=lang, content='')
        self.session.add(page_info)
        self.session.flush()
        return page_info

    def test_str_and_repr(self):
        self.assertEqual(str(self.create_pageinfo()),
                         "<PageInfo [1] 'Home' /it/index>")