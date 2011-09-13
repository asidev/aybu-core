#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
            for j in xrange(3,8):
                password = "".join(random.sample('%s%s' % (string.letters,
                                                           string.digits), j))

                user = User(username='test', password=password)
                self.session.add(user)
                self.session.commit()

                salt = user.password[0:2]
                crypted_password = crypt.crypt(password, salt)

                """
                self.assertEqual(crypted_password, user.password)
                """

                self.session.delete(user)
                self.session.commit()
