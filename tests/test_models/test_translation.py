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


class NodeInfoTests(BaseTests):

    def populate(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_data = data/default_data.json
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)

        populate(self.config, data)

    def test_create_translations(self):

        self.populate()

        language = self.session.query(Language).\
                        filter(Language.lang==u'en').one()
        language.enabled = False

        src_language = self.session.query(Language).\
                            filter(Language.lang==u'it').one()
        dst_language = self.session.query(Language).\
                            filter(Language.lang==u'de').one()

        dst_language.enabled = True

        translations = NodeInfo.create_translations(self.session,
                                                    src_language.id,
                                                    dst_language)

        original = self.session.query(NodeInfo).\
                        filter(NodeInfo.lang.has(id=src_language.id)).count()
        self.assertEqual(len(translations), original)

        original = self.session.query(NodeInfo).\
                        filter(NodeInfo.lang.has(id=language.id)).count()
        self.assertEqual(len(translations), original)

    def test_remove_translations(self):

        self.populate()

        language = self.session.query(Language).\
                        filter(Language.lang==u'it').one()
        language.enabled = False

        removed = NodeInfo.remove_translations(self.session, language.id)
        self.assertNotEqual(removed, 0)

        translations = self.session.query(NodeInfo).\
                            filter(NodeInfo.lang.has(id=language.id)).count()
        self.assertEqual(translations, 0)

    def test_menu_info_create_translation(self):

        self.populate()

        language = self.session.query(Language).\
                        filter(Language.lang==u'de').one()
        menu_info = self.session.query(MenuInfo).first()
        new_menu_info = menu_info.create_translation(language)
        self.assertNotEqual(menu_info, new_menu_info)
        self.assertNotEqual(menu_info.id, new_menu_info.id)
        self.assertNotEqual(menu_info.lang, new_menu_info.lang)
        self.assertEqual(new_menu_info.lang, language)
        self.assertEqual(menu_info.node, new_menu_info.node)

    def test_page_info_create_translation(self):

        self.populate()

        language = self.session.query(Language).\
                        filter(Language.lang==u'de').one()
        page_info = self.session.query(PageInfo).first()
        new_page_info = page_info.create_translation(language)
        self.assertNotEqual(page_info, new_page_info)
        self.assertNotEqual(page_info.id, new_page_info.id)
        self.assertNotEqual(page_info.lang, new_page_info.lang)
        self.assertEqual(new_page_info.lang, language)
        self.assertEqual(page_info.node, new_page_info.node)
        self.assertEqual(page_info.url, new_page_info.url)
        self.assertEqual(page_info.content, new_page_info.content)
        self.assertEqual(page_info.files, new_page_info.files)
        self.assertEqual(page_info.images, new_page_info.images)
        self.assertEqual(page_info.links, new_page_info.links)

    def test_section_info_create_translation(self):

        self.populate()

        language = self.session.query(Language).\
                        filter(Language.lang==u'de').one()
        info = self.session.query(SectionInfo).first()
        new_info = info.create_translation(language)
        self.assertNotEqual(info, new_info)
        self.assertNotEqual(info.id, new_info.id)
        self.assertNotEqual(info.lang, new_info.lang)
        self.assertEqual(new_info.lang, language)
        self.assertEqual(info.node, new_info.node)

    def test_external_link_info_create_translation(self):

        self.populate()

        language = self.session.query(Language).\
                        filter(Language.lang==u'de').one()
        info = self.session.query(ExternalLinkInfo).first()
        new_info = info.create_translation(language)
        self.assertNotEqual(info, new_info)
        self.assertNotEqual(info.id, new_info.id)
        self.assertNotEqual(info.lang, new_info.lang)
        self.assertEqual(new_info.lang, language)
        self.assertEqual(info.node, new_info.node)

    def test_internal_link_info_create_translation(self):

        self.populate()

        language = self.session.query(Language).\
                        filter(Language.lang==u'de').one()
        info = self.session.query(InternalLinkInfo).first()
        new_info = info.create_translation(language)
        self.assertNotEqual(info, new_info)
        self.assertNotEqual(info.id, new_info.id)
        self.assertNotEqual(info.lang, new_info.lang)
        self.assertEqual(new_info.lang, language)
        self.assertEqual(info.node, new_info.node)

    def test_property_type(self):

        self.populate()

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

    def test_on_update_url_part(self):

        self.populate()

        section = self.session.query(Section).filter(Section.id == 4).one()
        section_info = section.translations[0]
        page_5 = self.session.query(Page).filter(Page.id == 5).one()
        page_6 = self.session.query(Page).filter(Page.id == 6).one()
        page = self.session.query(Page).filter(Page.id == 9).one()
        page_10 = self.session.query(Page).filter(Page.id == 10).one()
        page_5_info = page_5.translations[0]
        page_6_info = page_6.translations[0]
        page_info = page.translations[0]
        page_10_info = page_10.translations[0]

        self.assertEqual(section_info.lang.lang, 'it')
        self.assertIn(page_5, section.children)
        self.assertIn(page_6, section.children)
        self.assertEqual(page_5_info.lang.lang, 'it')
        self.assertEqual(page_6_info.lang.lang, 'it')
        section_info.url_part = section_info.url_part + '_test'
        section_url = '{}/{}'.format(section_info.partial_url,
                                     section_info.url_part)
        self.assertEqual(section_url, page_5_info.partial_url)

        self.assertEqual(page_info.lang.lang, 'it')
        old_url = page_info.url
        page_10_info_old_url = page_10_info.url
        page_info.url_part = page_info.url_part + '_test'
        self.session.commit()
        self.assertNotEqual(page_info.url, old_url)

        self.assertIn(page_10, page.children)
        self.assertEqual(page_10_info.lang.lang, 'it')
        page_url = '{}/{}'.format(page_info.partial_url,  page_info.url_part)
        self.assertEqual(page_url, page_10_info.partial_url)
        self.assertNotEqual(page_10_info_old_url, page_10_info.url)



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
