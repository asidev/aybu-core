#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


class ValidationError(Exception):
    """This class must be used by validators when they fail during checks.

        'ValidationError' is equal to 'Exception',
        but its string representation is different because
        it force string formatting using self.args.
        String formatting can fail, in this case 'ValidationError.__repr__'
        return the same result of 'Exception.__repr__'.
    """
    def __init__(self, *args):
        super(ValidationError, self).__init__(*args)

    def __repr__(self):

        try:
            return self.args[0] % self.args[1:]

        except (TypeError, IndexError) as e:
            log.debug('String formatting fails: %s', e)
            return super(ValidationError, self).__repr__()

    def __str__(self):
        return self.__repr__()
