#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models import populate
from aybu.core.models import add_default_data
from aybu.core.models import default_data_from_config
from aybu.core.models import default_user_from_config
from aybu.core.models import engine_from_config_parser
from aybu.core.models import Setting
from logging import getLogger
from test_base import BaseTests
import ConfigParser
import json
import StringIO

log = getLogger(__name__)


class InitTests(BaseTests):

    def test_populate(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_data = data/default_data.json
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)

        populate(self.config, data)

    def test_engine_from_config_parser(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        self.assertRaises(KeyError, engine_from_config_parser, config)

        file_ = StringIO.StringIO(
"""
[app:aybu-website]
sqlalchemy.url = sqlite:///
sqlalchemy.echo = true
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        engine_from_config_parser(config)

    def test_default_data_from_config(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
sqlalchemy.url = sqlite:///
default_data =
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)
        self.assertEqual(data, None)

        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_data = data/default_data.json
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        data = default_data_from_config(config)
        self.assertNotEqual(data, None)

    def test_add_default_data(self):
        data = file('data/default_data.json').read()
        data = json.loads(data)
        add_default_data(self.session, data)

        self.assertIn(self.session.query(Setting).get('max_pages'),
                      self.session.query(Setting).all())

    def test_default_user_from_config(self):
        file_ = StringIO.StringIO(
"""
[app:aybu-website]
sqlalchemy.url = sqlite:///
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        self.assertRaises(ValueError, default_user_from_config, config)

        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_user =
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        self.assertRaises(ValueError, default_user_from_config, config)

        file_ = StringIO.StringIO(
"""
[app:aybu-website]
default_user.username = Pippo
default_user.password = Pippo
""")
        config = ConfigParser.ConfigParser()
        config.readfp(file_)
        user = default_user_from_config(config)
        self.assertEqual(user.username, 'Pippo')
        self.assertEqual(user.password, 'Pippo')