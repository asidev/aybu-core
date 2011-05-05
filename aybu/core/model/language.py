#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

from elixir import Entity, Field, Unicode, Integer, Boolean
from elixir import using_options, using_table_options
from sqlalchemy import UniqueConstraint


class Language(Entity):
    id = Field(Integer, primary_key=True)
    lang = Field(Unicode(2), required=True)
    country = Field(Unicode(2), required=True)
    enabled = Field(Boolean, default=True)

    using_table_options(UniqueConstraint('lang', 'country'))
    using_options(tablename="languages")

    def __str__(self):
        return "<Language %s_%s>" % (self.lang, self.country)

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
