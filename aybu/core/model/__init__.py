#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

"""The application's model objects"""

import elixir
from aybu.core.model.meta import dbsession, metadata

__all__ = ['init_model', 'dbsession', 'metadata']


def init_model(engine):
    metadata.bind = engine
    import aybu.core.model.entities
    elixir.setup_all()
    return dbsession, metadata
