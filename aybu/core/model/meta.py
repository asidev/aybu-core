#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import elixir
from pufferfish import HookableSession

__all__ = ['dbsession', 'metadata']

dbsession = HookableSession()
metadata = elixir.metadata
elixir.delay_setup = True
elixir.session = dbsession
