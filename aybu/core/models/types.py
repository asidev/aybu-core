#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import crypt
import sqlalchemy.types as types
import random

__all__ = ['Crypt']


class Crypt(types.TypeDecorator):
    """ This class model an encrypted string using UNiX crypt(3). """

    impl = types.CHAR

    def process_bind_param(self, value, dialect):
        return crypt.crypt(value, "".join(random.sample(string.letters, 2)))

    def process_result_value(self, value, dialect):
        return value

    
