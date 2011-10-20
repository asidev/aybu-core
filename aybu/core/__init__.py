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

__version__ = (0, 2, 0, 'dev', 0)

def includeme(config):
    # initialize pufferfish fsentity
    from aybu.core.models import File, Image, Banner
    base_path = config.registry.settings['pufferfish.base_path']
    private_path = config.registry.settings['pufferfish.private_path']
    for cls in (File, Image, Banner):
        cls.initialize(base_path, private_path)
