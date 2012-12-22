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

from aybu.core.models import add_default_data
from aybu.core.models import Setting
from aybu.core.testing import TransactionalTestsBase
import json
import pkg_resources



class InitTests(TransactionalTestsBase):


    def test_add_default_data(self):
        data = pkg_resources.resource_stream('aybu.core.data',
                                             'default_data.json').read()
        data = json.loads(data)
        add_default_data(self.session, data)

        self.assertIn(self.session.query(Setting).get('max_pages'),
                      self.session.query(Setting).all())
