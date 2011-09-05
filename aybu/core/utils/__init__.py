#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)

def get_object_from_python_path(path):
    """ Resolve 'path' and return the object identified by it. """

    if not isinstance(path, basestring):
        # 'path' can be a class instance. Convert it into a string.
        path = str(path)

    log.debug('Path: %s', path)

    elements = path.split('.')
    log.debug('Elements: %s', ' | '.join(elements))
    target = elements.pop(-1)
    log.debug('Target: %s', target)

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

        log.debug('Element: %s', element)
        log.debug('Imported: %s', imported)
        log.debug('Module: %s', module.__name__)

    if not hasattr(module, target):
        raise ValueError('Wrong Python path: no %s in %s.' % (target,
                                                              module.__name__))

    return getattr(module, target)
