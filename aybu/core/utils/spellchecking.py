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

__all__ = ["SpellChecker"]


class SpellChecker(object):
    """ Spellchecker using enchant """

    def __init__(self, lang):
        import enchant
        self.lang = "%s_%s" % (lang.lang, lang.country.upper())
        self.dictionary = enchant.Dict(self.lang)

    def checkWords(self, words):
        return [word for word in words if not self.dictionary.check(word)]

    def getSuggestions(self, word):
        return self.dictionary.suggest(word)
