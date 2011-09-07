#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.utils.exceptions import ValidationError
from aybu.core.models import View, ViewDescription, Language
from logging import getLogger
from test_base import BaseTests
try:
    import unittest2 as unittest
except:
    import unittest

log = getLogger(__name__)


class CryptTests(BaseTests):
    pass
