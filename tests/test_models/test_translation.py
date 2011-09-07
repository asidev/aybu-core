#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.utils.exceptions import ValidationError
from aybu.core.models import Menu, Page, NodeInfo, Language
from logging import getLogger
from test_base import BaseTests
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class NodeInfoTests(BaseTests):

    def test_str_and_repr(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page = Page(id=2, parent=menu, weight=1)
        self.session.add(page)
        lang = Language(lang=u'it', country=u'it')
        self.session.add(lang)

        node_info = NodeInfo(id=1, label='Home', title='Pagina Principale',
                             url_part='index', url='/it/index.html', node=page,
                             lang=lang)
        self.session.add(node_info)
        self.session.flush()

        self.assertEqual(str(node_info),
                         "<NodeInfo [1] 'Home' /it/index.html>")

    def test_get_by_url(self):
        menu = Menu(id=1, parent=None, weight=1)
        self.session.add(menu)
        page = Page(id=2, parent=menu, weight=1)
        self.session.add(page)
        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)

        node_info_1 = NodeInfo(id=1, label='Home', title='Pagina Principale',
                             url_part='index', url='/it/index.html', node=page,
                             lang=it)
        self.session.add(node_info_1)

        node_info_2 = NodeInfo(id=2, label='Home', title='Main Page',
                             url_part='index', url='/en/index.html', node=page,
                             lang=en)
        self.session.add(node_info_2)

        self.session.flush()

        self.assertEqual(node_info_1, NodeInfo.get_by_url(self.session,
                                                          '/it/index.html'))
        self.assertEqual(node_info_2, NodeInfo.get_by_url(self.session,
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

        node_info_1 = NodeInfo(id=1, label='Home', title='Pagina Principale',
                             url_part='index', url='/it/index.html', node=page_4,
                             lang=it)
        self.session.add(node_info_1)

        node_info_2 = NodeInfo(id=2, label='Home', title='Main Page',
                             url_part='index', url='/en/index.html', node=page_4,
                             lang=en)
        self.session.add(node_info_2)

        node_info_3 = NodeInfo(id=3, label='Home 2', title='Pagina Principale 2',
                             url_part='index', url='/it/index2.html', node=page_1,
                             lang=it)
        self.session.add(node_info_1)

        node_info_4 = NodeInfo(id=4, label='Home 2', title='Main Page 2',
                             url_part='index', url='/en/index2.html', node=page_1,
                             lang=en)
        self.session.add(node_info_2)

        self.session.flush()

        self.assertEqual(NodeInfo.get_homepage(self.session, it), node_info_1)
        self.assertEqual(NodeInfo.get_homepage(self.session, en), node_info_2)

        page_4.home = False

        self.assertEqual(NodeInfo.get_homepage(self.session, it), node_info_3)
        self.assertEqual(NodeInfo.get_homepage(self.session, en), node_info_4)
