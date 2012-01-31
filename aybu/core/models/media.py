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

from aybu.core.models import Page, PageInfo
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
import logging

__all__ = []
log = logging.getLogger(__name__)


class MediaPage(Page):
    __mapper_args__ = {'polymorphic_identity': 'media_page'}
    file_id = Column(Integer, ForeignKey('files.id',
                                         onupdate='cascade',
                                         ondelete='restrict'))
    file = relationship('File', lazy='joined')


class MediaCollectionPage(MediaPage):
    __mapper_args__ = {'polymorphic_identity': 'media_collection_page'}
    translations = relationship('MediaCollectionPageInfo', lazy='joined')


class MediaItemPage(MediaPage):
    __mapper_args__ = {'polymorphic_identity': 'media_item_page'}
    translations = relationship('MediaItemPageInfo', lazy='joined')


class MediaCollectionPageInfo(PageInfo):
    __mapper_args__ = {'polymorphic_identity': 'media_collection_page_info'}
    node = relationship('MediaCollectionPage', lazy='joined')


class MediaItemPageInfo(PageInfo):
    __mapper_args__ = {'polymorphic_identity': 'media_item_page_info'}
    node = relationship('MediaItemPage', lazy='joined')
