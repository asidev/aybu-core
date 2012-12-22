#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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

from aybu.core.models import (Menu,
                              Page,
                              PageInfo,
                              Language)
from logging import getLogger
from aybu.core.testing import TransactionalTestsBase


log = getLogger(__name__)


class PageInfoTests(TransactionalTestsBase):

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
