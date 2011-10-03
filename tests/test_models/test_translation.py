#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models import Menu, Page, PageInfo, Section, SectionInfo
from aybu.core.models import Language
from logging import getLogger
from test_base import BaseTests

log = getLogger(__name__)


class NodeInfoTests(BaseTests):

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
