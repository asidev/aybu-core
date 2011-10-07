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
from logging import getLogger
import unittest

log = getLogger(__name__)


class LoaderTests(unittest.TestCase):

    def test_get_object_from_python_path(self):

        from aybu.core.utils import get_object_from_python_path
        from aybu.core.models import Node
        from aybu.core.models import NodeInfo

        self.assertRaises(ValueError,
                          get_object_from_python_path, None)

        self.assertRaises(ValueError,
                          get_object_from_python_path, '')

        self.assertRaises(ValueError,
                          get_object_from_python_path, 'wrong_name')

        path = 'aybu.core.models.Node'
        self.assertEqual(Node,
                         get_object_from_python_path(path))

        path = 'aybu.core.models.NodeInfo'
        self.assertEqual(NodeInfo,
                         get_object_from_python_path(path))

        path = 'aybu.core.models.wrong_name'
        self.assertRaises(ValueError,
                          get_object_from_python_path, path)
