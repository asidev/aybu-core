#!/usr/bin/env python
# -*- coding: utf-8 -*-

import crypt
import sqlalchemy.types as types

from hashlib import sha1

__all__ = ['SHA1', 'Crypt']


class SHA1(types.TypeDecorator):
    """ This class model an encrypted (and fixed) string. """

    impl = types.CHAR
    digest_size = sha1().digest_size * 2

    def __init__(self, *args, **kwargs):
        super(SHA1, self).__init__(self.digest_size, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        return sha1(value).hexdigest()

    def process_result_value(self, value, dialect):
        return value

    def copy(self):
        return SHA1(self.impl.length)


class Crypt(types.TypeDecorator):
    """ This class model an encrypted string using UNiX crypt(3). """

    impl = types.CHAR
    digest_size = 16  # this seems to be fixed to 13 in python crypt()

    def __init__(self, *args, **kwargs):
        super(Crypt, self).__init__(self.digest_size, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        return crypt.crypt(value, value)

    def process_result_value(self, value, dialect):
        return value

    def copy(self):
        return Crypt(self.impl.length)
