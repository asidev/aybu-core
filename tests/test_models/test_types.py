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

import crypt
import random
import string
from aybu.core.models import User
from logging import getLogger
from test_base import BaseTests

log = getLogger(__name__)


class CryptTests(BaseTests):

    def test_crypt(self):

        for i in xrange(0, 100):
            for j in xrange(3, 8):
                password = "".join(random.sample('%s%s' % (string.letters,
                                                           string.digits), j))

                user = User(username='test', password=password)
                self.session.add(user)
                self.session.commit()

                salt = user.password[0:2]
                crypted_password = crypt.crypt(password, salt)

                self.assertEqual(crypted_password, user.password)

                self.session.delete(user)
                self.session.commit()
