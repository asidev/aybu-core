#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

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

import ConfigParser
import StringIO
import os
from aybu.core.models import engine_from_config_parser, create_session
from aybu.core.models import default_data_from_config
from aybu.core.models import populate, init_session_events
from aybu.core.models.base import Base
from logging import getLogger
import unittest

log = getLogger(__name__)


class BaseTests(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        ini = os.path.realpath(
                os.path.join(os.path.dirname(__file__),
                    "..", "..",
                    'tests.ini'))

        try:
            with open(ini) as f:
                self.config.readfp(f)

        except IOError:
            raise Exception("Cannot find configuration file '%s'" % ini)

        self.engine = engine_from_config_parser(self.config)
        self.Session = create_session(self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        self.Session.remove()
        Base.metadata.drop_all(self.engine)

    def populate(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_data = data/default_data.json
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)

        populate(self.config, data, session=self.session)
