#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """


from sqlalchemy.ext.declarative import declarative_base


__all__ = ['Base']


Base = declarative_base()


def get_sliced(query, start = None, limit = None):

    if not start is None and not limit is None:
        return query[start:start+limit]

    if not start is None:
        return query[start:]

    return query.all()
