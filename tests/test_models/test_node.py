#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models import Node
from logging import getLogger
from test_base import BaseTests
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class NodeTests(BaseTests):

    def test_get_by_enabled(self):

        for node in self.session.query(Node).all():
            self.assertIn(node, Node.get_by_enabled(self.session))

    def test_validates(self):
        node_1 = Node(id=5, parent=None, weight=1, children=[])
        node_2 = Node(id=69, parent=None, weight=1, children=[])
        #node_1.children.append(node_2)
        #node_2.parent = node_1
        #node_2.parent_id = 5
        #self.session.flush()
        raise NotImplementedError()
