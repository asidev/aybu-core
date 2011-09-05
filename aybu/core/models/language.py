#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from aybu.website.models.base import Base
from aybu.website.models.base import get_sliced
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

        return get_sliced(query, start, limit)

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
            locale = Locale(self.lang, self.country)
            yield locale

        except UnknownLocale as e:
            log.debug(e)

        try:
            locale = Locale(self.lang)
            yield locale

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
