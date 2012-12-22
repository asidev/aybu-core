#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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

__all__ = ['get_object_from_python_path']

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
