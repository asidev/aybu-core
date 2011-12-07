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

import json
import logging
import os
import pkg_resources
import unittest
from aybu.core.models import init_session_events
from aybu.core.models import (add_default_data,
                              Base,
                              User,
                              Group)
from paste.deploy.loadwsgi import appconfig
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker


class BaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ini = os.path.realpath(
                os.path.join(os.path.dirname(__file__),
                    "..", "..",
                    'tests.ini'))
        cls.config = appconfig("config:{}#aybu-core".format(ini))
        cls.engine = engine_from_config(cls.config, prefix='sqlalchemy.')
        cls.Session = sessionmaker(bind=cls.engine)
        cls.log = logging.getLogger("{}.{}".format(__name__, cls.__name__))
        Base.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.Session.close_all()
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        connection = self.engine.connect()
        self.trans = connection.begin()
        self.session = self.Session(bind=connection)
        init_session_events(session=self.session)

    def tearDown(self):
        self.trans.rollback()
        self.session.close()

    def populate(self):
        source_ = pkg_resources.resource_stream('aybu.core.data',
                                             'default_data.json')
        data = json.loads(source_.read())
        source_.close()
        add_default_data(self.session, data)
        user = User(username=self.config['default_user.username'],
                    password=self.config['default_user.password'])
        self.session.merge(user)
        group = Group(name=u'admin')
        group.users.append(user)
        self.session.merge(group)
        self.session.commit()

