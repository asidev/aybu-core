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

from aybu.core.utils.modifiers import boolify, urlify
from pyramid import testing
import logging
import unittest

log = logging.getLogger(__name__)


class ModifiersTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_boolify(self):

        for value in ('on', 'true', 'yes', 'ok', 'y'):
            self.assertTrue(boolify(value))

        for value in ('false', 'False', 'no', 'n', 'abc'):
            self.assertFalse(boolify(value))

    def test_urlfy(self):
        url = ' Pagina Principale '
        self.assertEqual(urlify(url), 'pagina_principale')

        url = ' Pagina\nPrincipale '
        self.assertEqual(urlify(url), 'pagina_principale')

        url = ' Pagina\rPrincipale '
        self.assertEqual(urlify(url), 'pagina_principale')

        url = ' Pagina Principale%&/'
        self.assertEqual(urlify(url), 'pagina_principale')

        xlate = {
            0xc0: 'A', 0xc1: 'A', 0xc2: 'A', 0xc3: 'A', 0xc4: 'A', 0xc5: 'A',
            0xc6: 'Ae', 0xc7: 'C',
            0xc8: 'E', 0xc9: 'E', 0xca: 'E', 0xcb: 'E',
            0xcc: 'I', 0xcd: 'I', 0xce: 'I', 0xcf: 'I',
            0xd1: 'N',
            0xd2: 'O', 0xd3: 'O', 0xd4: 'O', 0xd5: 'O', 0xd6: 'O',
            0xd9: 'U', 0xda: 'U', 0xdb: 'U', 0xdc: 'U',
            0xdd: 'Y',
            0xe0: 'a', 0xe1: 'a', 0xe2: 'a', 0xe3: 'a', 0xe4: 'a', 0xe5: 'a',
            0xe6: 'ae', 0xe7: 'c',
            0xe8: 'e', 0xe9: 'e', 0xea: 'e', 0xeb: 'e',
            0xec: 'i', 0xed: 'i', 0xee: 'i', 0xef: 'i',
            0xf1: 'n',
            0xf2: 'o', 0xf3: 'o', 0xf4: 'o', 0xf5: 'o', 0xf6: 'o',
            0xf9: 'u', 0xfa: 'u', 0xfb: 'u', 0xfc: 'u',
            0xfd: 'y', 0xff: 'y'}

        url =  ' Pagina Principale '
        for c in xlate.keys():
            url = url + unichr(c)

        urlified = 'pagina_principale_'
        for c in xlate.keys():
            urlified = urlified + xlate[c]

        urlified = urlified.lower()

        self.assertEqual(urlify(url), urlified)





