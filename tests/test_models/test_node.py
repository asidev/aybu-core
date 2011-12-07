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

from aybu.core.exc import ValidationError
from aybu.core.models import Node, Menu, Page, Section, InternalLink
from aybu.core.models import ExternalLink, View, Setting, SettingType
from aybu.core.models import Language, Banner, Image, File
from aybu.core.models import MenuInfo, PageInfo
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.sql import func
from logging import getLogger
from aybu.core.testing import TransactionalTestsBase

log = getLogger(__name__)


class NodeTests(TransactionalTestsBase):

    def setUp(self):
        super(NodeTests, self).setUp()
        Banner.initialize(base='/static', private='/static/private')
        File.initialize(base='/static', private='/static/private')
        Image.initialize(base='/static', private='/static/private')

    def test_property_type(self):

        self.populate(self.session)

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

    def test_get_translation(self):

        self.populate(self.session)

        it = self.session.query(Language).filter(Language.lang == 'it').one()
        en = self.session.query(Language).filter(Language.lang == 'en').one()
        es = self.session.query(Language).filter(Language.lang == 'es').one()

        home = Page.get_homepage(self.session)
        it_translation = home.get_translation(it)
        self.assertEqual(it_translation,
                         PageInfo.get_homepage(self.session, it))
        en_translation = home.get_translation(en)
        self.assertEqual(en_translation,
                         PageInfo.get_homepage(self.session, en))
        es_translation = home.get_translation(es)
        self.assertEqual(es_translation,
                         PageInfo.get_homepage(self.session, es))

    def test_before_flush(self):

        en = Language(id=2, lang="en", country="GB", enabled=True)
        menu = Menu(id=1, weight=1)
        self.session.add(menu)
        menu_info = MenuInfo(id=29, label=u"Main Menu", lang=en, node=menu)
        index = Page(id=2, home=True, parent=menu, weight=1)
        index_info = PageInfo(id=2, label="Home", title="Home Page",
                              url_part="index", content="<h2>Home Page</h2>",
                              lang=en, node=index)
        company = Page(id=3, home=True, parent=menu, weight=2)
        company_info = PageInfo(id=3, label="Company", title="Company",
                                url_part="company", content="<h2>Company</h2>",
                                lang=en, node=company)
        team = Page(id=4, home=True, parent=company, weight=3)
        team_info = PageInfo(id=4, label="Team", title="Team",
                              url_part="team", content="<h2>Team</h2>",
                              lang=en, node=team)
        dummy = Page(id=5, home=True, parent=menu, weight=4)

        parent_url = '/' + en.lang
        self.assertEqual(index_info.parent_url, parent_url)
        index_info_url = parent_url + '/' + index_info.url_part
        self.assertEqual(index_info.url, index_info_url)
        self.assertEqual(company_info.parent_url, parent_url)
        company_info_url = parent_url + '/' + company_info.url_part
        self.assertEqual(company_info.url, company_info_url)
        self.assertEqual(team_info.parent_url, company_info.url)
        team_info_url = company_info.url + '/' + team_info.url_part
        self.assertEqual(team_info.url, team_info_url)

        team_info = self.session.query(PageInfo).filter(PageInfo.id == 4).one()
        self.assertEqual(team_info.url, team_info_url)

        team.parent = menu
        self.session.flush()
        self.assertEqual(team_info.parent_url, parent_url)
        self.assertEqual(team_info.url, parent_url + '/' + team_info.url_part)

        team_info.node = dummy
        self.session.flush()
        team_info = self.session.query(PageInfo).filter(PageInfo.id == 4).one()
        self.assertEqual(team_info.url, parent_url + '/' + team_info.url_part)

    def test_before_flush_populate(self):

        self.populate(self.session)
        log.debug('Populate ended. Starting tests ...')

        menu = self.session.query(Menu).first()
        en = self.session.query(Language).filter(Language.lang == 'en').one()
        info = self.session.query(PageInfo).filter(PageInfo.id == 14).one()
        self.assertEqual(info.url, u'/en/company/our_history')
        team = Page(home=True, parent=info.node, weight=3)
        team_info = PageInfo(label="Team", title="The Team",
                             url_part="team",
                             content='<h2><a href="/en/company/our_history.html">History</a></h2>',
                             lang=en, node=team)
        self.session.flush()
        self.assertIn(info, team_info.links)
        self.assertEqual(team_info.parent_url, u'/en/company/our_history')
        self.assertIn(u'/en/company/our_history', team_info.content)
        self.assertIn(info, team_info.links)

        info.node.weight = 1000
        info.node.parent = menu
        self.session.flush()
        self.assertEqual(info.parent_url, u'/en')
        self.assertEqual(team_info.parent_url, u'/en/our_history')
        self.assertNotIn(u'/en/company/our_history', team_info.content)
        self.assertIn(u'/en/our_history', team_info.content)
        self.assertIn(info, team_info.links)

    def test_content_links_parsing(self):
        self.populate(self.session)
        en = self.session.query(Language).filter(Language.lang == 'en').one()
        menu = self.session.query(Menu).first()
        home_info = self.session.query(PageInfo).filter(PageInfo.id == 2).one()
        home = home_info.node
        contact_info = self.session.query(PageInfo).filter(PageInfo.id == 4).one()
        contact = contact_info.node
        team = Page(home=True, parent=menu, weight=300)
        content = '<h2>'
        content += '<a href="{obj.url}">{obj.label}</a>'.format(obj=home_info)
        content += '</h2>'
        team_info = PageInfo(label="Team", title="The Team",
                             url_part="team",
                             content=content,
                             lang=en, node=team)
        self.session.flush()
        self.assertIn(home_info, team_info.links)
        self.assertNotIn(contact_info, team_info.links)

        content = '<a href="{obj.url}">{obj.label}</a>'.format(obj=contact_info)
        team_info.content = team_info.content + content
        self.session.flush()
        self.assertIn(home_info, team_info.links)
        self.assertIn(contact_info, team_info.links)
        self.assertIn(home_info.url, team_info.content)
        self.assertIn(contact_info.url, team_info.content)

        home.weight = 3000
        home.parent = self.session.query(Section).filter(Section.id == 4).one()
        log.debug('Flushing...')
        self.session.flush()
        self.assertIn(home_info.url, team_info.content)
        self.assertIn(contact_info.url, team_info.content)
        self.assertIn(home_info, team_info.links)
        self.assertIn(contact_info, team_info.links)


class PageTests(TransactionalTestsBase):

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


class InternalLinkTests(TransactionalTestsBase):

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
