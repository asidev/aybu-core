#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import os
from aybu.core.models import engine_from_config_parser, create_session
from aybu.core.models.base import Base
from logging import getLogger
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import unittest

log = getLogger(__name__)


class BaseTests(unittest.TestCase):

    def setUp(self):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'tests.ini'))

        self.engine = engine_from_config_parser(config)
        self.session = create_session(self.engine)


    def tearDown(self):
        self.session.remove()
        Base.metadata.drop_all(self.engine)
