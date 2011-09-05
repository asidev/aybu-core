#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models.base import Base
from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)

class BaseTests(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.session.remove()
        Base.metadata.drop_all(self.engine)
