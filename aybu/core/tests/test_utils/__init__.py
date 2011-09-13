#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
