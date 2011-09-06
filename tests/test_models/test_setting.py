#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models import Page
from aybu.core.models import Setting
from aybu.core.models import SettingType
from aybu.core.utils.exceptions import ConstraintError
from logging import getLogger
from test_base import BaseTests
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class SettingTests(BaseTests):

    def test_check_max_pages(self):

        max_pages = Setting(name=u'max_pages',
                            value=u'1',
                            ui_administrable=False,
                            type=SettingType(name=u'integer',
                                             raw_type=u'int'))
        self.session.add(max_pages)

        self.assertEqual(Setting.check_max_pages(self.session), None)

        page = Page(id=1, weight=0)
        self.session.add(page)

        self.assertRaises(ConstraintError,
                          Setting.check_max_pages,
                          self.session)
