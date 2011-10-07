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

from aybu.core.models import Menu, MenuInfo, Page, PageInfo
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


class NodeInfoTests(BaseTests):

    def test_property_type(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_data = data/default_data.json
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)

        populate(self.config, data)

        menu_info = self.session.query(MenuInfo).\
                         order_by(func.random()).first()
        self.assertEqual(menu_info.type, 'MenuInfo')

        page_info = self.session.query(PageInfo).\
                         order_by(func.random()).first()
        self.assertEqual(page_info.type, 'PageInfo')

        section_info = self.session.query(SectionInfo).\
                            order_by(func.random()).first()
        self.assertEqual(section_info.type, 'SectionInfo')

        external_link_info = self.session.query(ExternalLinkInfo).\
                                  order_by(func.random()).first()
        self.assertEqual(external_link_info.type, 'ExternalLinkInfo')

        internal_link_info = self.session.query(InternalLinkInfo).\
                                  order_by(func.random()).first()
        self.assertEqual(internal_link_info.type, 'InternalLinkInfo')

    def test_str_and_repr(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        section = Section(id=2, parent=menu, weight=1)
        self.session.add(section)
        lang = Language(lang=u'it', country=u'it')
        self.session.add(lang)

        section_info = SectionInfo(id=1, label='Azienda', title='Azienda',
                             url_part='azienda', node=section, lang=lang)
        self.session.add(section_info)
        self.session.flush()

        self.assertEqual(str(section_info),
                         "<SectionInfo [1] 'Azienda'>")

    def test_get_by_url(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page = Page(id=2, parent=menu, weight=1)
        self.session.add(page)
        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)

        page_info_1 = PageInfo(id=1, label='Home', title='Pagina Principale',
                             url_part='index', url='/it/index.html', node=page,
                             lang=it)
        self.session.add(page_info_1)

        page_info_2 = PageInfo(id=2, label='Home', title='Main Page',
                             url_part='index', url='/en/index.html', node=page,
                             lang=en)
        self.session.add(page_info_2)

        self.session.flush()

        self.assertEqual(page_info_1, PageInfo.get_by_url(self.session,
                                                          '/it/index.html'))
        self.assertEqual(page_info_2, PageInfo.get_by_url(self.session,
                                                          '/en/index.html'))

    def test_get_homepage(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page_1 = Page(id=2, parent=menu, weight=1)
        self.session.add(page_1)
        page_2 = Page(id=3, parent=menu, weight=2)
        self.session.add(page_2)
        page_3 = Page(id=4, parent=menu, weight=3)
        self.session.add(page_3)
        page_4 = Page(id=5, parent=menu, weight=4, home=True)
        self.session.add(page_4)

        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)

        page_info_1 = PageInfo(id=1, label='Home', title='Pagina Principale',
                               url_part='index', url='/it/index.html',
                               node=page_4, lang=it)
        self.session.add(page_info_1)

        page_info_2 = PageInfo(id=2, label='Home', title='Main Page',
                               url_part='index', url='/en/index.html',
                               node=page_4, lang=en)
        self.session.add(page_info_2)

        page_info_3 = PageInfo(id=3, label='Home 2',
                               title='Pagina Principale 2',
                               url_part='index', url='/it/index2.html',
                               node=page_1, lang=it)
        self.session.add(page_info_1)

        page_info_4 = PageInfo(id=4, label='Home 2', title='Main Page 2',
                             url_part='index', url='/en/index2.html',
                             node=page_1, lang=en)
        self.session.add(page_info_2)

        self.session.flush()

        self.assertEqual(PageInfo.get_homepage(self.session, it), page_info_1)
        self.assertEqual(PageInfo.get_homepage(self.session, en), page_info_2)

        page_4.home = False

        self.assertEqual(PageInfo.get_homepage(self.session, it), page_info_3)
        self.assertEqual(PageInfo.get_homepage(self.session, en), page_info_4)


class PageInfoTests(BaseTests):

    def test_str_and_repr(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page = Page(id=2, parent=menu, weight=1)
        self.session.add(page)
        lang = Language(lang=u'it', country=u'it')
        self.session.add(lang)

        page_info = PageInfo(id=1, label='Home', title='Pagina Principale',
                             url_part='index', url='/it/index.html', node=page,
                             lang=lang)
        self.session.add(page_info)
        self.session.flush()

        self.assertEqual(str(page_info),
                         "<PageInfo [1] 'Home' /it/index.html>")
