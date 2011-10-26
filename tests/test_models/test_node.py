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

from aybu.core.exc import ValidationError
from aybu.core.models import Node, Menu, Page, Section, InternalLink
from aybu.core.models import ExternalLink, View, Setting, SettingType
from aybu.core.models import Language
from aybu.core.models import MenuInfo, PageInfo, SectionInfo, ExternalLinkInfo
from aybu.core.models import InternalLinkInfo
from aybu.core.models import default_data_from_config
from aybu.core.models import populate
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.sql import func
from logging import getLogger
from test_base import BaseTests

log = getLogger(__name__)


class NodeTests(BaseTests):

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

        menu = self.session.query(Menu).\
                    order_by(func.random()).first()
        self.assertEqual(menu.type, 'Menu')

        page = self.session.query(Page).\
                    order_by(func.random()).first()
        self.assertEqual(page.type, 'Page')

        section = self.session.query(Section).\
                       order_by(func.random()).first()
        self.assertEqual(section.type, 'Section')

        external_link = self.session.query(ExternalLink).\
                             order_by(func.random()).first()
        self.assertEqual(external_link.type, 'ExternalLink')

        internal_link = self.session.query(InternalLink).\
                             order_by(func.random()).first()
        self.assertEqual(internal_link.type, 'InternalLink')

    def test_str_and_repr(self):

        node = Menu(id=1, weight=1)
        self.assertEqual(str(node),
                         '<Menu id="1" parent="None" weight="1" />')

        node2 = Node(id=2, parent=node, weight=1)
        self.assertEqual(str(node2),
                         '<Node id="2" parent="1" weight="1" />')

    def test_get_by_id(self):

        node = Node(id=1, weight=0)
        node2 = Node(id=2, weight=1)
        self.session.add(node)
        self.session.add(node2)

        self.assertEqual(Node.get_by_id(self.session, 1), node)
        self.assertEqual(Node.get_by_id(self.session, 2), node2)

    def test_get_by_enabled(self):

        node1 = Node(id=1, weight=10, enabled=True)
        self.session.add(node1)
        node2 = Node(id=2, weight=20, enabled=False)
        self.session.add(node2)
        node3 = Node(id=3, weight=30, enabled=True)
        self.session.add(node3)
        node4 = Node(id=4, weight=40, enabled=False)
        self.session.add(node4)

        self.assertIn(node1, Node.get_by_enabled(self.session, True))
        self.assertIn(node3, Node.get_by_enabled(self.session, True))
        self.assertIn(node2, Node.get_by_enabled(self.session, False))
        self.assertIn(node4, Node.get_by_enabled(self.session, False))
        self.assertEqual(len(Node.get_by_enabled(self.session, True)), 2)
        self.assertEqual(len(Node.get_by_enabled(self.session,
                                                 False, start=0, limit=0)), 0)
        self.assertEqual(len(Node.get_by_enabled(self.session,
                                                 False, start=0, limit=1)), 1)
        self.assertEqual(len(Node.get_by_enabled(self.session,
                                                 False, start=0, limit=2)), 2)
        self.assertEqual(len(Node.get_by_enabled(self.session,
                                                 False, start=1)), 1)
        self.assertEqual(len(Node.get_by_enabled(self.session,
                                                 False, start=2)), 0)
        self.assertEqual(len(Node.get_by_enabled(self.session,
                                                 False, start=-1)), 1)

    def test_get_max_weight(self):
        node1 = Menu(id=1, weight=10)
        self.session.add(node1)
        node2 = Page(id=2, parent=node1, weight=20)
        self.session.add(node2)
        node3 = Page(id=3, parent=node2, weight=30)
        self.session.add(node3)

        self.assertEqual(Node.get_max_weight(self.session, parent=None), 10)
        self.assertEqual(Node.get_max_weight(self.session, parent=node1), 20)
        self.assertEqual(Node.get_max_weight(self.session, parent=node2), 30)
        # Node.get_max_weight return None when the query is empty.
        self.assertEqual(Node.get_max_weight(self.session, parent=node3), None)

    def test_validate_parent_for_menu(self):
        menu = Menu(id=1, parent=None)
        page = Page(id=2, parent=menu)
        section = Section(id=3, parent=menu)
        external_link = ExternalLink(id=4, parent=menu)
        internal_link = InternalLink(id=5, parent=menu)

        # Menu can only have None as parent
        for parent in (menu, page, section, external_link, internal_link,
                       'test', [], {}):
            self.assertRaises(ValidationError, Menu, parent=parent)

    def test_validate_invalid_parent(self):
        menu = Menu(id=1, parent=None)
        """
        page = Page(id=2, parent=menu)
        section = Section(id=3, parent=menu)
        """
        external_link = ExternalLink(id=4, parent=menu)
        internal_link = InternalLink(id=5, parent=menu)
        # Nodes different from Menu can only have page, section and Menu as
        # parent
        for parent in (None, external_link, internal_link):
            self.assertRaises(ValidationError, Page, parent=parent)
            self.assertRaises(ValidationError, Section, parent=parent)
            self.assertRaises(ValidationError, ExternalLink, parent=parent)
            self.assertRaises(ValidationError, InternalLink, parent=parent)

    def test_validate_invalid_children(self):
        menu = Menu(id=1, parent=None)
        page = Page(id=2, parent=menu)
        section = Section(id=3, parent=menu)
        external_link = ExternalLink(id=4, parent=menu)
        internal_link = InternalLink(id=5, parent=menu)
        for node in (external_link, internal_link):
            with self.assertRaises(ValidationError):
                node.children = [page, section]

    def test_validate_valid_children(self):
        menu = Menu(id=1, parent=None)
        page = Page(id=2, parent=menu)
        section = Section(id=3, parent=menu)
        """
        external_link = ExternalLink(id=4, parent=menu)
        internal_link = InternalLink(id=5, parent=menu)
        """

        child_page = Page(id=6, parent=menu)
        child_section = Section(id=7, parent=menu)

        another_menu = Menu(id=8, parent=None)
        another_page = Page(id=9, parent=menu)
        another_section = Section(id=10, parent=menu)

        for node in (another_menu, another_page, another_section):
            node.children = [child_page, child_section]

        for node in (menu, page, section):
            menu.children.append(child_page)
            menu.children.append(child_section)

    def test_create(self):

        with self.assertRaises(ValidationError):
            Node.create(self.session, id=1, parent=None, weight=1)

        menu = Menu.create(self.session, id=1, parent=None)
        #page = Page.create(self.session, id=2, parent=menu)
        Page.create(self.session, id=2, parent=menu)
        # TODO test create when finished to be implemented

    def test_get_translation(self):

        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_data = data/default_data.json
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)

        populate(self.config, data)

        it = self.session.query(Language).filter(Language.lang == 'it').one()
        en = self.session.query(Language).filter(Language.lang == 'en').one()
        es = self.session.query(Language).filter(Language.lang == 'es').one()

        home = Page.get_homepage(self.session)
        it_translation = home.get_translation(self.session, it)
        self.assertEqual(it_translation,
                         PageInfo.get_homepage(self.session, it))
        en_translation = home.get_translation(self.session, en)
        self.assertEqual(en_translation,
                         PageInfo.get_homepage(self.session, en))
        es_translation = home.get_translation(self.session, es)
        self.assertEqual(es_translation,
                         PageInfo.get_homepage(self.session, es))

        page = self.session.query(Page).order_by(func.random()).first()
        it_page_info = self.session.query(PageInfo).\
                                 filter(PageInfo.node == page).\
                                 filter(PageInfo.lang == it).one()
        self.assertEqual(it_page_info, page.get_translation(self.session, it))
        en_page_info = self.session.query(PageInfo).\
                                 filter(PageInfo.node == page).\
                                 filter(PageInfo.lang == en).one()
        self.assertEqual(en_page_info, page.get_translation(self.session, en))
        es_page_info = self.session.query(PageInfo).\
                                 filter(PageInfo.node == page).\
                                 filter(PageInfo.lang == es).one()
        self.assertEqual(es_page_info, page.get_translation(self.session, es))

        menu = self.session.query(Menu).first()
        it_menu_info = self.session.query(MenuInfo).\
                               filter(MenuInfo.node == menu).\
                               filter(MenuInfo.lang == it).one()
        self.assertEqual(it_menu_info, menu.get_translation(self.session, it))
        en_menu_info = self.session.query(MenuInfo).\
                               filter(MenuInfo.node == menu).\
                               filter(MenuInfo.lang == en).one()
        self.assertEqual(en_menu_info, menu.get_translation(self.session, en))
        es_menu_info = self.session.query(MenuInfo).\
                               filter(MenuInfo.node == menu).\
                               filter(MenuInfo.lang == es).one()
        self.assertEqual(es_menu_info, menu.get_translation(self.session, es))

        section = self.session.query(Section).order_by(func.random()).first()
        it_section_info = self.session.query(SectionInfo).\
                               filter(SectionInfo.node == section).\
                               filter(SectionInfo.lang == it).one()
        self.assertEqual(it_section_info,
                         section.get_translation(self.session, it))
        en_section_info = self.session.query(SectionInfo).\
                               filter(SectionInfo.node == section).\
                               filter(SectionInfo.lang == en).one()
        self.assertEqual(en_section_info,
                         section.get_translation(self.session, en))
        es_section_info = self.session.query(SectionInfo).\
                               filter(SectionInfo.node == section).\
                               filter(SectionInfo.lang == es).one()
        self.assertEqual(es_section_info,
                         section.get_translation(self.session, es))

        external_link = self.session.query(ExternalLink).\
                             order_by(func.random()).first()
        it_external_link_info = self.session.query(ExternalLinkInfo).\
                               filter(ExternalLinkInfo.node == external_link).\
                               filter(ExternalLinkInfo.lang == it).one()
        self.assertEqual(it_external_link_info,
                         external_link.get_translation(self.session, it))
        en_external_link_info = self.session.query(ExternalLinkInfo).\
                               filter(ExternalLinkInfo.node == external_link).\
                               filter(ExternalLinkInfo.lang == en).one()
        self.assertEqual(en_external_link_info,
                         external_link.get_translation(self.session, en))
        es_external_link_info = self.session.query(ExternalLinkInfo).\
                               filter(ExternalLinkInfo.node == external_link).\
                               filter(ExternalLinkInfo.lang == es).one()
        self.assertEqual(es_external_link_info,
                         external_link.get_translation(self.session, es))

        internal_link = self.session.query(InternalLink).\
                             order_by(func.random()).first()
        it_internal_link_info = self.session.query(InternalLinkInfo).\
                               filter(InternalLinkInfo.node == internal_link).\
                               filter(InternalLinkInfo.lang == it).one()
        self.assertEqual(it_internal_link_info,
                         internal_link.get_translation(self.session, it))
        en_internal_link_info = self.session.query(InternalLinkInfo).\
                               filter(InternalLinkInfo.node == internal_link).\
                               filter(InternalLinkInfo.lang == en).one()
        self.assertEqual(en_internal_link_info,
                         internal_link.get_translation(self.session, en))
        es_internal_link_info = self.session.query(InternalLinkInfo).\
                               filter(InternalLinkInfo.node == internal_link).\
                               filter(InternalLinkInfo.lang == es).one()
        self.assertEqual(es_internal_link_info,
                         internal_link.get_translation(self.session, es))

        self.session.delete(it_page_info)
        self.session.delete(en_page_info)
        self.session.delete(es_page_info)
        self.assertEqual(None, page.get_translation(self.session, it))
        self.assertEqual(None, page.get_translation(self.session, en))
        self.assertEqual(None, page.get_translation(self.session, es))


class PageTests(BaseTests):

    def test_get_homepage(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page_1 = Page(id=2, parent=menu, weight=1, home=True)
        self.session.add(page_1)
        page_2 = Page(id=3, parent=menu, weight=2)
        self.session.add(page_2)
        page_3 = Page(id=4, parent=menu, weight=3)
        self.session.add(page_3)
        page_4 = Page(id=5, parent=menu, weight=4)
        self.session.add(page_4)

        self.assertEqual(page_1, Page.get_homepage(self.session))

        page_2.home = True

        with self.assertRaises(MultipleResultsFound):
            Page.get_homepage(self.session)

        page_1.home = False
        self.assertEqual(page_2, Page.get_homepage(self.session))

        page_2.home = False
        self.assertEqual(page_1, Page.get_homepage(self.session))

        page_1.home = False
        section = Section(id=6, parent=menu, weight=5)
        self.session.add(section)
        page_1.parent = section
        page_2.parent = section
        page_3.parent = section
        page_4.parent = section

        self.assertIn(Page.get_homepage(self.session), (page_1, page_2, page_3,
                                                        page_4))

    def test_set_homepage(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page_1 = Page(id=2, parent=menu, weight=1, home=True)
        self.session.add(page_1)
        page_2 = Page(id=3, parent=menu, weight=2)
        self.session.add(page_2)
        page_3 = Page(id=4, parent=menu, weight=3)
        self.session.add(page_3)
        page_4 = Page(id=5, parent=menu, weight=4)
        self.session.add(page_4)

        self.assertEqual(page_1, Page.get_homepage(self.session))

        Page.set_homepage(self.session, page_2)
        self.assertEqual(page_2, Page.get_homepage(self.session))

    def test_validate_homepage(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        i = 2
        for home in ('on', 'true', 'yes', 'ok', 'y'):
            Page(id=i, parent=menu, weight=i - 1, home=home)
            i = i + 1

        for home in ('false', 'abc', 'no', 'n', 'False', False):
            Page(id=i, parent=menu, weight=i - 1, home=home)
            i = i + 1

    def test_validate_view(self):
        view = View(id=1, name=u'TEST VIEW', fs_view_path=u'/pages/full.mako')
        self.session.add(view)
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page_1 = Page(id=2, parent=menu, weight=1, view=view, home=True)
        self.session.add(page_1)

        for v in (None, {}, [], ''):
            with self.assertRaises(ValidationError):
                Page(id=3, parent=menu, weight=1, view=v, home=True)

    def test_validate_sitemap_priority(self):

        max_pages = Setting(name=u'max_pages',
                            value=u'100',
                            ui_administrable=False,
                            type=SettingType(name=u'integer',
                                             raw_type=u'int'))
        self.session.add(max_pages)

        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)

        for i in xrange(1, 101):
            page = Page(id=i, parent=menu, weight=i, sitemap_priority=i)
            self.session.add(page)

        with self.assertRaises(ValidationError):
            page = Page(id=150, parent=menu, weight=101, sitemap_priority=150)

        with self.assertRaises(ValidationError):
            page = Page(id=151, parent=menu, weight=102, sitemap_priority=-5)

    def test_is_last_page(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page_1 = Page(id=2, parent=menu, weight=1)
        self.session.add(page_1)

        self.assertEqual(True, Page.is_last_page(self.session))

        page_2 = Page(id=3, parent=menu, weight=2)
        self.session.add(page_2)

        self.assertEqual(False, Page.is_last_page(self.session))

    def test_new_page_allowed(self):

        max_pages = Setting(name=u'max_pages',
                            value=u'1',
                            ui_administrable=False,
                            type=SettingType(name=u'integer',
                                             raw_type=u'int'))
        self.session.add(max_pages)

        self.assertTrue(Page.new_page_allowed(self.session))

        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page = Page(id=2, parent=menu, home=True, weight=1)
        self.session.add(page)

        self.assertFalse(Page.new_page_allowed(self.session))

        page_2 = Page(id=3, parent=menu, weight=2)
        self.session.add(page_2)

        self.assertFalse(Page.new_page_allowed(self.session))


class InternalLinkTests(BaseTests):

    def test_validate_linked_to(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)

        page = Page(id=2, parent=menu, home=True, weight=1)
        self.session.add(page)

        internal_link = InternalLink(id=3, parent=menu, weight=2,
                                     linked_to=page)
        self.session.add(internal_link)

        with self.assertRaises(ValidationError):
            internal_link.linked_to = menu
