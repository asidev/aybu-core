#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.utils.exceptions import ValidationError
from aybu.core.models import Node, Menu, Page, Section, InternalLink
from aybu.core.models import ExternalLink
from logging import getLogger
from test_base import BaseTests
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class NodeTests(BaseTests):

    def test_property_type(self):

        node = Node(id=1)
        self.assertEqual(node.type, 'Node')

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
        menu = Menu(parent=None)
        page = Page(parent=menu)
        section = Section(parent=menu)
        external_link = ExternalLink(parent=menu)
        internal_link = InternalLink(parent=menu)

        # Menu can only have None as parent
        for parent in (menu, page, section, external_link, internal_link,
                       'test', [], {}):
            self.assertRaises(ValidationError, Menu, parent=parent)

    def test_validate_invalid_parent(self):
        menu = Menu(parent=None)
        page = Page(parent=menu)
        section = Section(parent=menu)
        external_link = ExternalLink(parent=menu)
        internal_link = InternalLink(parent=menu)
        # Nodes different from Menu can only have page, section and Menu as
        # parent
        for parent in (None, external_link, internal_link):
            self.assertRaises(ValidationError, Page, parent=parent)
            self.assertRaises(ValidationError, Section, parent=parent)
            self.assertRaises(ValidationError, ExternalLink, parent=parent)
            self.assertRaises(ValidationError, InternalLink, parent=parent)

    def test_validate_invalid_children(self):
        menu = Menu(parent=None)
        page = Page(parent=menu)
        section = Section(parent=menu)
        external_link = ExternalLink(parent=menu)
        internal_link = InternalLink(parent=menu)
        for node in (external_link, internal_link):
            with self.assertRaises(ValidationError):
                node.children = [page, section]

    def test_validate_valid_children(self):
        menu = Menu(parent=None)
        page = Page(parent=menu)
        section = Section(parent=menu)
        external_link = ExternalLink(parent=menu)
        internal_link = InternalLink(parent=menu)
        for node in (menu, page, section):
            node.children = [page, section]

