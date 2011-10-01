#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import os
from aybu.core.models import engine_from_config_parser, create_session
from aybu.core.models.base import Base
from logging import getLogger
import unittest

log = getLogger(__name__)


class BaseTests(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.ConfigParser()

        try:
            ini = os.path.realpath(
                    os.path.join(os.path.dirname(__file__),
                        "..", "..", "..", "..",
                        'tests.ini'))
            with open(ini) as f:
                self.config.readfp(f)
        except IOError:

            raise Exception("Cannot find configuration at '%s'" % ini)

        self.engine = engine_from_config_parser(self.config)
        self.session = create_session(self.engine)

    def tearDown(self):
        self.session.remove()
        Base.metadata.drop_all(self.engine)
