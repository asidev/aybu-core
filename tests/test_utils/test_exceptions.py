#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.utils.exceptions import BaseError
from pyramid import testing
import logging
import unittest

log = logging.getLogger(__name__)


class ExceptionsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_base_error(self):

        error = BaseError()
        self.assertEqual(str(error), 'BaseError()')

        message = 'Message'
        error = BaseError(message)
        self.assertEqual(str(error), message)

        error = BaseError('Message', 'Arg 1', 'Arg 2')
        self.assertEqual(str(error),
                         "BaseError('Message', 'Arg 1', 'Arg 2')")

        args = ('Error: %s, %s', 'arg1', 'arg2')
        error = BaseError(*args)
        self.assertEqual(str(error), args[0] % (args[1], args[2]))
