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

import json
import logging
import os
import pkg_resources
import pyramid.testing
import unittest
from aybu.core.request import Request
from aybu.core.models import init_session_events
from aybu.core.models import (add_default_data,
                              Base,
                              User,
                              Group)
from paste.deploy.loadwsgi import appconfig
from sqlalchemy import engine_from_config
from sqlalchemy.orm import (sessionmaker,
                            Session)
from webtest import TestApp

from nose.plugins import Plugin

config = None


class ReadAybuConfigPlugin(Plugin):
    """ Nose plugin that parses an aybu config """
    name = 'aybu-config'
    enabled = False
    score = None
    log = logging.getLogger('nose.plugins.aybu')

    def options(self, parser, env=os.environ):
        parser.add_option('--aybu-config', action='store',
                          dest='aybu_config', default=None,
                          help='Path to the tests ini')
        super(ReadAybuConfigPlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(ReadAybuConfigPlugin, self).configure(options, conf)
        if not self.enabled:
            return

        if options.aybu_config:
            self.load_config(options.aybu_config)
        else:
            self.load_config("tests.ini")

    def load_config(self, option):
        try:
            configfile, section = option.split('#', 1)
            uri = "config:{}#{}".format(os.path.realpath(configfile), section)
        except ValueError:
            uri = "config:{}".format(os.path.realpath(option))

        try:
            self.config = appconfig(uri)

            global config
            config = self.config

        except Exception as e:
            import sys
            print "Cannot load config from {}: {}".format(uri, e)
            sys.exit(2)


class TestsBase(unittest.TestCase):

    @classmethod
    def create_tables(cls, drop=False):
        if drop:
            cls.drop_tables()
        Base.metadata.create_all(cls.engine)

    @classmethod
    def drop_tables(cls):
        Base.metadata.drop_all(cls.engine)

    @classmethod
    def initialize(cls, config):
        cls.config = config

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'config') and config:
            cls.config = config
        cls.engine = engine_from_config(cls.config, prefix='sqlalchemy.')
        cls.log = logging.getLogger("{}.{}".format(__name__, cls.__name__))
        cls.create_tables()

    @classmethod
    def tearDownClass(cls):
        cls.drop_tables()

    def populate(self, session=None):
        SessionFactory = None
        if not session:
            SessionFactory = sessionmaker(bind=self.engine)
            session = SessionFactory()

        source_ = pkg_resources.resource_stream('aybu.core.data',
                                             'default_data.json')
        data = json.loads(source_.read())
        source_.close()
        add_default_data(session, data)
        user = User(username=self.config['default_user.username'],
                    password=self.config['default_user.password'])
        session.merge(user)
        group = Group(name=u'admin')
        group.users.append(user)
        session.merge(group)
        session.commit()

        if SessionFactory:
            session.close()
            SessionFactory.close_all()


class TransactionalTestsBase(TestsBase):

    @classmethod
    def setUpClass(cls):
        super(TransactionalTestsBase, cls).setUpClass()
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()
        self.session = self.Session(bind=self.connection)
        init_session_events(session=self.session)

    def tearDown(self):
        self.trans.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        super(TransactionalTestsBase, cls).tearDownClass()
        cls.Session.close_all()


class UnitTestsBase(TransactionalTestsBase):

    def setUp(self):
        super(UnitTestsBase, self).setUp()
        Request.set_db_session(self.connection, self.Session)
        self.req = Request({})
        self.ctx = pyramid.testing.DummyResource
        self.configurator = pyramid.testing.setUp(request=self.req)
        self.req.registry = self.configurator.registry
        self.configurator.include('pyramid_mailer.testing')

    def tearDown(self):
        pyramid.testing.tearDown()
        super(UnitTestsBase, self).tearDown()


class FunctionalTestsBase(TestsBase):

    def setUp(self):
        self.create_tables(drop=True)
        self.populate()
        app = self.get_wsgi_app()
        self.testapp = TestApp(app)
        self.login()

    def get_wsgi_app(self):
        raise NotImplementedError

    def tearDown(self):
        Session.close_all()
        self.drop_tables()

    def login(self):
        params = dict(submit='yes',
                      username=self.config['default_user.username'],
                      password=self.config['default_user.password'])
        response = self.testapp.post('/admin/login.html',
                                     params)
        response = response.follow(status=200)


