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

from aybu.core.models.base import Base
from aybu.core.models.setting import Setting
from aybu.core.models.translation import NodeInfo
from aybu.core.exc import QuotaError
from babel import Locale
from babel.core import UnknownLocaleError as UnknownLocale
from logging import getLogger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy import Unicode


__all__ = ['Language']
log = getLogger(__name__)


class Language(Base):

    __tablename__ = 'languages'
    __table_args__ = (UniqueConstraint('lang', 'country'),
                      {'mysql_engine': 'InnoDB'})

    id = Column(Integer, primary_key=True)
    lang = Column(Unicode(2), nullable=False)
    country = Column(Unicode(2), nullable=False)
    enabled = Column(Boolean, default=True)

    def __repr__(self):
        return "<Language %s_%s [%s]>" % (self.lang,
                                          self.country,
                                          "enabled" if self.\
                                                    enabled else "disabled")

    def __setattr__(self, attr, value):
        if attr == u"lang":
            value = value.lower()
        elif attr == u"country":
            value = value.upper()
        super(Language, self).__setattr__(attr, value)

    def __eq__(self, other):
        return self.lang == other.lang and self.country == other.country

    @classmethod
    def get_by_lang(cls, session, lang):
        criterion = cls.lang.ilike(lang)
        return session.query(cls).filter(criterion).first()

    @classmethod
    def get_by_enabled(cls, session, enabled=None, start=None, limit=None):

        query = session.query(cls)

        if not enabled is None:
            query = query.filter(cls.enabled == enabled)

        return cls.slice_query(query, start, limit)

    @property
    def locale(self):

        try:
            return Locale(self.lang, self.country)
        except UnknownLocale as e:
            log.debug(e)

        try:
            return Locale(self.lang)
        except UnknownLocale as e:
            log.debug(e)

        return None

    @property
    def locales(self):

        try:
            l = Locale(self.lang, self.country)
            yield l
        except UnknownLocale as e:
            log.debug(e)

        try:
            l = Locale(self.lang)
            yield l
        except UnknownLocale as e:
            log.debug(e)

    @classmethod
    def get_locales(cls, session, enabled=None, strict=False):
        """ Create an iterator upon the list of available languages."""
        for language in cls.get_by_enabled(session, enabled):

            if strict:
                yield language.locale
                continue

            for locale in language.locales:
                yield locale

    @classmethod
    def enable(cls, session, id_, translation_lang_id):
        """ Enable the language 'id_'
            if the number of enabled languages did not reach 'max_languages',
            then create translations for that language:
            create translations for each NodeInfo
            from 'translation_lang_id' to 'lang_id'.
        """
        max_ = Setting.get(session, 'max_languages').value
        enabled = cls.count(session, Language.enabled == True)
        if enabled >= max_:
            msg = 'The maximum number of enabled languages was reached.'
            raise QuotaError(msg)

        language = cls.get(session, id_)
        language.enabled = True

        NodeInfo.create_translations(session,
                                     translation_lang_id,
                                     language)

        return language

    @classmethod
    def disable(cls, session, id_):
        """ Disable the language 'id_'
            if it is not the only enabled one,
            then delete all translations for that language.
        """

        if Language.count(session, cls.enabled == True) < 2:
            raise QuotaError('Cannot disable last enabled language.')

        language = Language.get(session, id_)
        language.enabled = False

        NodeInfo.remove_translations(session, id_)

        return language
