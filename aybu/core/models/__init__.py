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
from sqlalchemy.util.langhelpers import symbol
import json

log = getLogger(__name__)


__all__ = ['populate', 'engine_from_config_parser', 'create_session',
           'add_default_data', 'default_data_from_config',
           'default_user_from_config', 'Base', 'Banner', 'Image', 'File',
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
        sqlalchemy.event.listen(class_.parent_url,
                                'set',
                                Base.on_attr_update)
        sqlalchemy.event.listen(class_.url_part,
                                'set',
                                Base.on_attr_update)
        sqlalchemy.event.listen(class_.node_id,
                                'set',
                                Base.on_attr_update)

    elif class_ is Section or class_ is Page:
        sqlalchemy.event.listen(class_.parent_id, 'set', Base.on_attr_update)


def init_session_events(session=Session):
    sqlalchemy.event.listen(session, 'before_flush', PageInfo.before_flush)
    sqlalchemy.event.listen(session, 'after_flush', after_flush)


def after_flush(session, *args):
    """ Set 'parent_url' and update it when 'url_part' was changed.
    """

    nones = (symbol('NO_VALUE'), symbol('NEVER_SET'), None)

    # Handle 'parent_id' changes in Page and Section objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in [obj
                for obj in session
                if isinstance(obj, (Page, Section)) and \
                   hasattr(obj, '_attrs_updates') and \
                   'parent_id' in obj._attrs_updates]:

        for t in obj.translations:

            if isinstance(obj.parent, (Section, Page)):
                t.parent_url = obj.parent.get_translation(t.lang).url
            else:
                t.parent_url = '/{}'.format(t.lang.lang)

    # Handle 'node' changes in CommonInfo objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in [obj
                for obj in session
                if isinstance(obj, CommonInfo) and \
                   hasattr(obj, '_attrs_updates') and \
                   'node_id' in obj._attrs_updates]:

        node = Node.get(session, obj._attrs_updates['node_id']['new'])

        if isinstance(obj.node.parent, (Section, Page)):
            obj.parent_url = obj.node.parent.get_translation(obj.lang).url
        else:
            obj.parent_url = '/{}'.format(obj.lang.lang)

    # Handle 'parent_url' changes in CommonInfo objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in [obj
                for obj in session
                if isinstance(obj, CommonInfo) and \
                   hasattr(obj, '_attrs_updates') and \
                   'parent_url' in obj._attrs_updates]:

        old = obj._attrs_updates['parent_url']['old']
        new = obj._attrs_updates['parent_url']['new']

        if old in nones or not obj.node.children:
            continue

        # Update children in the URL tree.
        criterion = CommonInfo.parent_url.ilike(old + '%')
        for item in session.query(CommonInfo).filter(criterion).all():
            # FIXME!!!
            # Handle 'url' changes in PageInfo objects:
            # replace links in PageInfo objects that referer them.
            if isinstance(item, PageInfo): pass

            item.parent_url = item.parent_url.replace(old, new, 1)

    # Handle 'url_part' changes in CommonInfo objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in [obj
                for obj in session
                if isinstance(obj, CommonInfo) and \
                   hasattr(obj, '_attrs_updates') and \
                   'url_part' in obj._attrs_updates]:

        old = obj._attrs_updates['url_part']['old']

        if old not in nones or not obj.node.children:
            continue

        old_url = '{}/{}'.format(obj.parent_url, old)
        new_url = '{}/{}'.format(obj.parent_url, new)

        # Update children in the URL tree.
        criterion = CommonInfo.parent_url.ilike(old_url + '%')
        for item in session.query(CommonInfo).filter(criterion).all():
            # FIXME!!!
            # Handle 'url' changes in PageInfo objects:
            # replace links in PageInfo objects that referer them.
            if isinstance(item, PageInfo): pass

            item.parent_url = item.parent_url.replace(old_url,
                                                      new_url,
                                                      1)


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
