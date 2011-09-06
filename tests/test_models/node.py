#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
from base import BaseTests
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class NodeTests(BaseTests):

    def test_get_by_enabled(self):
        fill_db(self.session)

        for node in self.session.query(Node).all():
            self.assertIn(node, Node.get_by_enabled(self.session))
