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

from aybu.core.models import (User, Language)
from babel import Locale
from logging import getLogger
from pyramid.decorator import reify
from pyramid.request import Request as BaseRequest
from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.security import unauthenticated_userid
from sqlalchemy import create_engine
from sqlalchemy.orm import (scoped_session,
                            sessionmaker,
                            joinedload)
import locale

__all__ = []

log = getLogger(__name__)


class Request(BaseRequest):

    db_engine = None
    Session = None

    def __init__(self, *args, **kwargs):

        super(Request, self).__init__(*args, **kwargs)

        if not self.db_engine is None:
            self.db_session = self.Session()
            self.db_session.configure(bind=self.db_engine)

        self.add_finished_callback(self.finished_callback)

        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        self.translation_factory = TranslationStringFactory('aybu-website')

        self._locale_name = None
        self._language = None
        self._localizer = None

    @reify
    def user(self):
        # Query.get or session.merge are the same.
        # Using Query.get you can set earger loading options!
        # FIXME: move query inside model!
        userid = unauthenticated_userid(self)
        if userid is None:
            return None
        query = self.db_session.query(User).options(joinedload('groups'))
        return query.get(userid)

    @reify
    def _settings(self):
        return self.registry.settings

    @classmethod
    def set_db_engine(cls, engine):

        if isinstance(engine, basestring):
            engine = create_engine(engine)

        cls.db_engine = engine
        cls.Session = scoped_session(sessionmaker(bind=engine))

    @property
    def locale_name(self):
        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html

        if not self._locale_name is None:
            return self._locale_name

        for loc in self.accepted_locales:
            return str(loc)

    @locale_name.setter
    def locale_name(self, loc_name):
        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        self._locale_name = loc_name
        log.debug('Set request.locale_name: %s', self._locale_name)
        self._localizer = get_localizer(self)
        log.debug('Set request.localizer: %s', self._localizer)
        log.debug('Set locale: %s.UTF8', self._locale_name)
        locale.setlocale(locale.LC_ALL, '%s.UTF8' % self._locale_name)

    @property
    def language(self):

        if self._language is None:
            self.set_language_to_default()

        return self._language

    @language.setter
    def language(self, lang): 
        log.debug('Set language: %s', lang)
        self._language = lang
        self.locale_name = str(lang.locale)

    @property
    def languages(self):

        languages_ = list(self.accept_language)
        default = self.registry.settings['default_locale_name']

        if default not in languages_:
            # It is usefull when client didn't send any AcceptLanguage header.
            # then default language will be the default locale.
            languages_.append(default)

        for language in languages_:
            yield language

    @property
    def accepted_locales(self):
        for language in self.languages:
            sep = '-' if '-' in language else '_'
            try:
                yield Locale.parse(language, sep)

            except Exception as e:
                log.debug(e)

    @property
    def localizer(self):

        if self._localizer is None and self._language is None:
            self.set_language_to_default()

        return self._localizer

    @localizer.setter
    def localizer(self, localizer):
        self._localizer = localizer

    def translate(self, string):
        """ This function will be exported to templates as '_' """
        return self.localizer.translate(self.translation_factory(string))

    def finished_callback(self, request):
        """ It clears the database session. """
        self.db_session.close()
        self.Session.remove()

    def set_language_to_default(self):
        # USE language.setter!
        self.language = Language.\
                        get_by_lang(self.db_session,
                                    self._settings['default_locale_name'])
