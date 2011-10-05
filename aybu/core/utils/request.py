#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.core.models import User
from babel import Locale
from logging import getLogger
from pyramid.decorator import reify
from pyramid.request import Request as BaseRequest
from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.security import unauthenticated_userid
from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
import locale

__all__ = []

log = getLogger(__name__)


class Request(BaseRequest):

    db_engine = None
    db_session = None

    def __init__(self, *args, **kwargs):

        super(Request, self).__init__(*args, **kwargs)

        self.db_session = scoped_session(sessionmaker())

        if not self.db_engine is None:
            self.db_session.configure(bind=self.db_engine)

        self.add_finished_callback(self.finished_callback)

        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        self.translation_factory = TranslationStringFactory('aybu-website')

        self._locale_name = None
        self._language = None
        self.localizer = None

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

    @classmethod
    def set_db_engine(cls, engine):

        if isinstance(engine, basestring):
            engine = create_engine(engine)

        cls.db_engine = engine

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
        self.localizer = get_localizer(self)
        log.debug('Set request.localizer: %s', self.localizer)
        log.debug('Set locale: %s.UTF8', self._locale_name)
        locale.setlocale(locale.LC_ALL, '%s.UTF8' % self._locale_name)

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, lang):
        log.debug('Set language: %s', lang)
        self._language = lang
        self.locale_name = str(lang.locale)

    @property
    def languages(self):

        languages_ = self.accept_language.best_matches()
        for language in languages_:
            yield language

            language = language[:2]
            if language not in languages_:
                yield language

    @property
    def accepted_locales(self):
        for language in self.languages:
            sep = '-' if '-' in language else '_'
            try:
                yield Locale.parse(language, sep)

            except Exception as e:
                log.debug(e)

    def translate(self, string):
        """ This function will be exported to templates as '_' """
        return self.localizer.translate(self.translation_factory(string))

    def finished_callback(self, request):
        """ It clears the database session. """
        self.db_session.remove()
        self.db_session.close()
