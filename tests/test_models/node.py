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

    def test_me(self): pass
