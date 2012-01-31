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

from logging import getLogger
from aybu.core.models.base import Base
from aybu.core.models.file import (Banner,
                                   File,
                                   Image,
                                   Logo)
from aybu.core.models.language import Language
from aybu.core.models.node import (ExternalLink,
                                   InternalLink,
                                   Menu,
                                   Node,
                                   Page,
                                   Section)
from aybu.core.models.translation import (MenuInfo,
                                          NodeInfo,
                                          CommonInfo,
                                          PageInfo,
                                          SectionInfo,
                                          ExternalLinkInfo,
                                          InternalLinkInfo)
from aybu.core.models.setting import (Setting,
                                      SettingType)
from aybu.core.models.theme import (Keyword,
                                    Theme)
from aybu.core.models.user import (User,
                                   Group)
from aybu.core.models.view import (View,
                                   ViewDescription)
from aybu.core.utils import get_object_from_python_path
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import Session
import sqlalchemy.orm
import sqlalchemy.event
from sqlalchemy.util.langhelpers import symbol

log = getLogger(__name__)


__all__ = ['add_default_data', 'Base', 'Banner', 'Image', 'File',
           'Language', 'ExternalLink', 'InternalLink', 'Menu', 'Node', 'Page',
           'Section', 'MenuInfo', 'NodeInfo', 'PageInfo', 'SectionInfo',
           'ExternalLinkInfo', 'InternalLinkInfo', 'Setting', 'SettingType',
           'Keyword', 'Theme', 'User', 'Group', 'View', 'ViewDescription']


@sqlalchemy.event.listens_for(sqlalchemy.orm.mapper, 'mapper_configured')
def init_attrs_events(mapper, class_):
    """
    Since Mixins are used, and mixins are not mapped classes, their attributes
    are normal Column objects, not InstrumentedAttribute instances that accept
    the 'set' event. We then set the "mapper_configured"  event, and, after
    the mapping phase, all events are set.
    """

    if class_ is Banner or class_ is Logo:
        sqlalchemy.event.listen(class_.default, 'set', class_.set_default)

    elif class_ is Image:
        sqlalchemy.event.listen(Image.name, 'set', Image.on_name_update)

    elif class_ is SectionInfo or class_ is PageInfo:
        sqlalchemy.event.listen(class_.url_part,
                                'set',
                                Base.on_attr_update)
        sqlalchemy.event.listen(class_.node,
                                'set',
                                Base.on_attr_update)
        if class_ is PageInfo:
            sqlalchemy.event.listen(class_.content,
                                    'set',
                                    Base.on_attr_update)

    elif class_ is Section or class_ is Page:
        sqlalchemy.event.listen(class_.parent_id, 'set', Base.on_attr_update)


def init_session_events(session=Session):
    sqlalchemy.event.listen(session, 'before_flush', before_flush)


def before_flush(session, *args):
    """ Set 'parent_url' and update it when 'url_part' was changed.
    """

    nones = (symbol('NO_VALUE'), symbol('NEVER_SET'), None)

    # NOTE: cannot know objects order in session.new and session.dirty,
    #       for that reason multiple 'for' cicles are needed.

    # Handle 'CommonInfo.parent_url' for 'new' objects.
    for obj in session.new:

        if not isinstance(obj, CommonInfo):
            continue

        if obj.node is None and obj.node_id is None:
            msg = '{} object must belong to a Node.'
            msg = msg.format(obj.__class__.__name__)
            raise ValueError(msg)

        elif obj.node is None:
            obj.node = Node.get(session, obj.node_id)

        #log.debug("Update 'parent_url' of %s", obj.label)
        obj.update_parent_url()

    # Handle 'PageInfo.content' for 'new' objects.
    for obj in session.new:

        if not isinstance(obj, PageInfo):
            continue

        #log.debug("Update associations of %s", obj.label)
        obj.update_associations()

    # Handle 'PageInfo.content' for 'new' objects.
    for obj in session.dirty:

        if not isinstance(obj, PageInfo) or \
           not hasattr(obj, '_attrs_updates') or \
           'content' not in obj._attrs_updates:
            continue

        #log.debug("Update associations of %s", obj.label)
        obj.update_associations()

    # First phase.
    # Handle 'node' changes in CommonInfo objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in session.dirty:

        if not isinstance(obj, CommonInfo) or \
           not hasattr(obj, '_attrs_updates') or \
           'node' not in obj._attrs_updates:
            continue

        obj.update_parent_url()

    # Second phase: handle Page|Section objects changes.
    # Handle 'parent_id' changes in Page and Section objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in session.dirty:

        if not isinstance(obj, (Page, Section)) or \
           not hasattr(obj, '_attrs_updates') or \
           'parent_id' not in obj._attrs_updates:
            continue

        #log.debug('Update translations of %s', obj.id)

        for translation in obj.translations:
            #log.debug('Update translation: %s', translation.label)
            translation.update_parent_url()

    # Third phase: handle CommonInfo.url_part changes.
    # Handle 'url_part' changes in CommonInfo objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in session.dirty:

        if not isinstance(obj, CommonInfo) or \
           not hasattr(obj, '_attrs_updates') or \
           'url_part' not in obj._attrs_updates:
            continue

        old = obj._attrs_updates['url_part']['old']
        new = obj._attrs_updates['url_part']['new']

        if old not in nones or old == new:
            continue

        obj.update_children_parent_url()


def add_default_data(session, data):

    for params in data:

        cls = 'aybu.core.models.%s' % params.pop('cls_')
        cls = get_object_from_python_path(cls)
        mapper = class_mapper(cls)

        for key, value in params.iteritems():

            if not value is None:

                try:
                    property_ = mapper.get_property(key)
                    #log.debug('property: %s', property_)
                except:
                    continue

                if not hasattr(property_, 'argument'):
                    continue

                try:
                    class_ = property_.argument.class_
                except AttributeError:
                    class_ = property_.argument()

                #log.debug('class: %s', class_)

                query = session.query(class_)

                if not property_.uselist and len(mapper.primary_key) == 1:
                    params[key] = query.get(value)
                    #log.debug('param: %s', params[key])
                    continue

                #log.debug('param was not updated: %s', params[key])
        """
                # The code below is needed when data specifies relationships
                # as list or scalar of primary keys.
                # This feature is not needed now.
                if not property_.uselist:
                    for i, col in enumerate(mapper.primary_key):
                        attr = getattr(class_, col.name)
                        query = query.filter(attr == value[i])
                    params[key] = query.one()
                    continue

                if len(mapper.primary_key) == 1:
                    values = []
                    for elem in value:
                        attr = getattr(class_, mapper.primary_key[0].name)
                        values.append(query.filter(attr == elem).one())
                    params[key] = values
                    continue

                values = []
                for elem in value:
                    for i, col in enumerate(mapper.primary_key):
                        attr = getattr(class_, col.name)
                        values.append(query.filter(attr == elem[i]).one())
                params[key] = values
        """

        obj = cls(**params)
        obj = session.merge(obj)
