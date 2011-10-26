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

import logging

log = logging.getLogger(__name__)


class BaseError(Exception):
    """'BaseError' is equal to 'Exception',
        but its string representation is different because
        it force string formatting using self.args.
        String formatting can fail, in this case 'ValidationError.__repr__'
        return the same result of 'Exception.__repr__'.
    """
    def __init__(self, *args):
        super(BaseError, self).__init__(*args)

    def __repr__(self):

        try:
            return self.args[0] % self.args[1:]

        except (TypeError, IndexError) as e:
            log.debug('String formatting fails: %s', e)
            return super(BaseError, self).__repr__()

    def __str__(self):
        return self.__repr__()


class ValidationError(BaseError):
    """This class must be used by validators when they fail during checks."""


class QuotaError(BaseError):
    """ This class must be used by Setting validators
        when they fail during checks.
    """


class ConstraintError(BaseError):
    """ Raise when an app-level constraint has been detected """
