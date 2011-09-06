#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models import add_default_data
from aybu.core.models import Page
from aybu.core.models import Setting
from aybu.core.models import SettingType
from aybu.core.utils.exceptions import ConstraintError
from logging import getLogger
from test_base import BaseTests
import json
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class InitTests(BaseTests):

    def test_add_default_data(self):
        data = file('data/default_data.json').read()
        data = json.loads(data)
        add_default_data(self.session, data)

        self.assertIn(self.session.query(Setting).get('max_pages'),
                      self.session.query(Setting).all())
        
