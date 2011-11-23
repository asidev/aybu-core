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
from logging import getLogger
from pyramid.decorator import reify
from pyramid.request import Request as PyramidRequest
from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.security import unauthenticated_userid
from sqlalchemy import create_engine
from sqlalchemy.orm import (scoped_session,
                            sessionmaker)

__all__ = ['Request', 'BaseRequest']
log = getLogger(__name__)


class BaseRequest(PyramidRequest):

    db_engine = None
    DBScopedSession = None

    def __init__(self, *args, **kwargs):

        super(BaseRequest, self).__init__(*args, **kwargs)

        self.db_session = self.DBScopedSession()
        self.add_finished_callback(self._finished_callback)
        self._session = None

    def _finished_callback(self, request):
        self.db_session.close()
        self.DBScopedSession.remove()

    @property
    def user(self):
        userid = unauthenticated_userid(self)
        return None if userid is None else User.get(self.db_session, userid)

    @reify
    def _settings(self):
        return self.registry.settings

    @classmethod
    def set_db_engine(cls, engine, **kwargs):

        if isinstance(engine, basestring):
            engine = create_engine(engine)

        cls.db_engine = engine
        # FIXME: add a uwsgi post-fork hook to recreate this session
        # per-process
        cls.DBScopedSession = scoped_session(sessionmaker(engine, **kwargs))


class Request(BaseRequest):

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)

        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        # FIXME: take the 'egg' from ini!
        self.translation_factory = TranslationStringFactory('aybu-website')

        self._locale_name = None
        self._language = None
        self._localizer = None

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
        import locale

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
            self.set_language_from_session_or_default()

        return self._language

    @language.setter
    def language(self, lang):
        self._language = lang
        self.locale_name = str(lang.locale)
        if self.user:
            if 'lang' in self.session:
                if self.session['lang'] == lang:
                    return
            log.debug("Saving language %s in session", lang)
            self.session['lang'] = lang

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
        from babel import Locale

        for language in self.languages:
            sep = '-' if '-' in language else '_'
            try:
                yield Locale.parse(language, sep)

            except Exception as e:
                log.debug(e)

    @property
    def localizer(self):

        if self._localizer is None and self._language is None:
            self.set_language_from_session_or_default()

        return self._localizer

    @localizer.setter
    def localizer(self, localizer):
        self._localizer = localizer

    def translate(self, string):
        """ This function will be exported to templates as '_' """
        return self.localizer.translate(self.translation_factory(string))

    def set_language_from_session_or_default(self):
        # USE language.setter!
        if self.user and 'lang' in self.session:
            log.debug("Getting language from session")
            lang = self.db_session.merge(self.session['lang'])
            log.debug("Got language %s", lang)
        else:
            lang = Language.\
                        get_by_lang(self.db_session,
                                    self._settings['default_locale_name'])
        self.language = lang
