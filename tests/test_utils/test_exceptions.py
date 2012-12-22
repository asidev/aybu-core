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
from aybu.core.exc import BaseError
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
