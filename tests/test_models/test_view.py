#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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

from aybu.core.models import View, ViewDescription, Language
from logging import getLogger
from aybu.core.testing import TransactionalTestsBase

log = getLogger(__name__)


class ViewTests(TransactionalTestsBase):

    def test_str_and_repr(self):
        view = View(id=1, name='TEST VIEW', fs_view_path='/pages/full.mako')
        self.session.add(view)
        self.session.flush()

        self.assertEqual(str(view), "<View TEST VIEW (/pages/full.mako)>")


class ViewDescriptionTests(TransactionalTestsBase):

    def test_str_and_repr(self):
        view = View(id=1, name='TEST VIEW', fs_view_path='/pages/full.mako')

        it = Language(lang=u'it', country=u'it')
        self.session.add(it)
        en = Language(lang=u'en', country=u'gb')
        self.session.add(en)

        view_description_it = ViewDescription(description='Descrizione test',
                                              view=view, language=it)
        view_description_en = ViewDescription(description='Test description',
                                              view=view, language=en)
        self.session.add(view_description_it)
        self.session.add(view_description_en)
        self.session.flush()

        self.assertEqual(str(view_description_it),
                         "<ViewDescription Descrizione test>")
        self.assertEqual(str(view_description_en),
                         "<ViewDescription Test description>")
