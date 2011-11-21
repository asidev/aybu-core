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

__all__ = ['Base', 'File', 'Image', 'Banner', 'Logo', 'Language',
           'Node', 'Menu', 'Page', 'Section', 'ExternalLink', 'InternalLink',
           'MenuInfo', 'NodeInfo', 'PageInfo', 'SectionInfo',
           'ExternalLinkInfo', 'InternalLinkInfo', 'Setting', 'SettingType',
           'Keyword', 'Theme', 'User', 'Group', 'View', 'ViewDescription']

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
from sqlalchemy import engine_from_config
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import sqlalchemy.orm
import sqlalchemy.event
import json

log = getLogger(__name__)


__all__ = ['populate', 'engine_from_config_parser', 'create_session',
           'add_default_data', 'default_data_from_config',
           'default_user_from_config', 'Base', 'Banner', 'Image', 'File',
           'Language', 'ExternalLink', 'InternalLink', 'Menu', 'Node', 'Page',
           'Section', 'MenuInfo', 'NodeInfo', 'PageInfo', 'SectionInfo',
           'ExternalLinkInfo', 'InternalLinkInfo', 'Setting', 'SettingType',
           'Keyword', 'Theme', 'User', 'Group', 'View', 'ViewDescription']


@sqlalchemy.event.listens_for(sqlalchemy.orm.mapper, "after_configured")
def _listens_for():
    """
    Since Mixins are used, and mixins are not mapped classes, their attributes
    are normal Column objects, not InstrumentedAttribute instances that accept
    the 'set' event. We then set the "mapper_configured"  event, and, after
    the mapping phase, all events are set.
    """

    sqlalchemy.event.listen(Banner.default, 'set', Banner.set_default)
    sqlalchemy.event.listen(Logo.default, 'set', Logo.set_default)
    sqlalchemy.event.listen(Session, 'before_flush',
                            PageInfo.before_flush)
    sqlalchemy.event.listen(Image.name, 'set', Image.on_name_update)
    # Add events needed to keep synchronized 'parent_url' columns.
    sqlalchemy.event.listen(SectionInfo.url_part, 'set',
                            CommonInfo.on_attr_update)
    sqlalchemy.event.listen(PageInfo.url_part, 'set', CommonInfo.on_attr_update)
    sqlalchemy.event.listen(SectionInfo.node, 'set', CommonInfo.on_attr_update)
    sqlalchemy.event.listen(PageInfo.node, 'set', CommonInfo.on_attr_update)
    sqlalchemy.event.listen(Session, 'after_flush', CommonInfo.after_flush)


def populate(config, data, config_section="app:main", session=None,
             drop_all=True):
    engine = engine_from_config_parser(config, config_section)
    if session is None:
        session = create_session(engine, drop_all)
        close_session = True
    else:
        close_session = False

    add_default_data(session, data)
    user = default_user_from_config(config)
    session.merge(user)

    group = Group(name=u'admin')
    group.users.append(user)
    session.merge(group)

    session.commit()
    if close_session:
        session.close()


def engine_from_config_parser(config, section="app:main"):

    options = {opt: config.get(section, opt)
               for opt in config.options(section)
               if opt.startswith("sqlalchemy.")}

    return engine_from_config(options)


def create_session(engine, drop_all=True):

    session = scoped_session(sessionmaker())
    session.configure(bind=engine)

    if drop_all:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    return session


def add_default_data(session, data):

    for params in data:

        cls = 'aybu.core.models.%s' % params.pop('cls_')
        cls = get_object_from_python_path(cls)
        mapper = class_mapper(cls)

        for key, value in params.iteritems():

            if not value is None:

                try:
                    property_ = mapper.get_property(key)
                except:
                    continue

                if not hasattr(property_, 'argument'):
                    continue

                try:
                    class_ = property_.argument.class_
                except AttributeError:
                    class_ = property_.argument()

                query = session.query(class_)

                if not property_.uselist and len(mapper.primary_key) == 1:
                    attr = getattr(class_, mapper.primary_key[0].name)
                    params[key] = query.filter(attr == value).one()
                    continue
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


def default_data_from_config(config):

    for section in config.sections():
        for option in config.options(section):

            if not option.startswith('default_data'):
                continue

            file_ = str(config.get(section, option))

            if not file_:
                continue

            data = open(file_).read()
            return json.loads(data)


def default_user_from_config(config):

    options = {}

    for section in config.sections():
        for option in config.options(section):

            if not option.startswith('default_user'):
                continue
            elif option.startswith('default_user.username'):
                key = 'username'
            elif option.startswith('default_user.password'):
                key = 'password'

            value = unicode(config.get(section, option))

            if not value:
                continue

            options[key] = value

    if not options:
        raise ValueError('No default user in configuration file!')

    return User(**options)
