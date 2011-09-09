#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.utils.exceptions import ValidationError
from aybu.core.models import View, ViewDescription, Language
from logging import getLogger
from test_base import BaseTests
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class ViewTests(BaseTests):

    def test_str_and_repr(self):
        view = View(id=1, name='TEST VIEW', fs_view_path='/pages/full.mako')
        self.session.add(view)
        self.session.flush()

        self.assertEqual(str(view), "<View TEST VIEW (/pages/full.mako)>")


class ViewDescriptionTests(BaseTests):

    def test_str_and_repr(self):
        view = View(id=1, name='TEST VIEW', fs_view_path='/pages/full.mako')

        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)

        view_description_it = ViewDescription(description='Descrizione di test',
                                              view=view, language=it)
        view_description_en = ViewDescription(description='Test description',
                                              view=view, language=en)
        self.session.add(view_description_it)
        self.session.add(view_description_en)
        self.session.flush()

        self.assertEqual(str(view_description_it),
                         "<ViewDescription Descrizione di test>")
        self.assertEqual(str(view_description_en),
                         "<ViewDescription Test description>")
