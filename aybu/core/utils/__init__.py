#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


def get_object_from_python_path(path):
    """ Resolve 'path' and return the object identified by it. """

    # 'path' can be a class instance. Convert it into a string.
    path = str(path)
    elements = path.split('.')
    target = elements.pop(-1)

    if not elements:
        raise ValueError('Wrong Python path: %s', path)

    imported = ''
    while elements:

        element = elements.pop(0)

        if imported:
            module = getattr(__import__(imported,
                                        globals(), locals(), [element], -1),
                             element)
            imported += '.' + element

        else:
            module = __import__(element)
            imported += element

    if not hasattr(module, target):
        raise ValueError('Wrong Python path: no %s in %s.' % (target,
                                                              module.__name__))

    return getattr(module, target)
