#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Base', 'File', 'Image', 'Banner', 'Language',
           'Node', 'Menu', 'Page', 'Section', 'ExternalLink', 'InternalLink',
           'MenuInfo', 'NodeInfo', 'PageInfo', 'SectionInfo', 'ExternalLinkInfo',
           'InternalLinkInfo', 'Setting', 'SettingType', 'Keyword', 'Theme',
           'User', 'Group', 'View', 'ViewDescription']

from logging import getLogger
from aybu.core.models.base import Base
from aybu.core.models.file import Banner
from aybu.core.models.file import File
from aybu.core.models.file import Image
from aybu.core.models.language import Language
from aybu.core.models.node import ExternalLink
from aybu.core.models.node import InternalLink
from aybu.core.models.node import Menu
from aybu.core.models.node import Node
from aybu.core.models.node import Page
from aybu.core.models.node import Section
from aybu.core.models.translation import MenuInfo
from aybu.core.models.translation import NodeInfo
from aybu.core.models.translation import PageInfo
from aybu.core.models.translation import SectionInfo
from aybu.core.models.translation import ExternalLinkInfo
from aybu.core.models.translation import InternalLinkInfo
from aybu.core.models.setting import Setting
from aybu.core.models.setting import SettingType
from aybu.core.models.theme import Keyword
from aybu.core.models.theme import Theme
from aybu.core.models.user import Group
from aybu.core.models.user import User
from aybu.core.models.view import View
from aybu.core.models.view import ViewDescription
from aybu.core.utils import get_object_from_python_path
from sqlalchemy import engine_from_config
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import json

log = getLogger(__name__)


def populate(config, data, config_section="app:main", session=None):
    engine = engine_from_config_parser(config, config_section)
    if session is None:
        session = create_session(engine)
        close_session = True
    else:
        close_session = False

    add_default_data(session, data)
    user = default_user_from_config(config)
    session.add(user)

    group = Group(name=u'admin')
    group.users.append(user)
    session.add(group)

    session.commit()
    if close_session:
        session.close()


def engine_from_config_parser(config, section="app:main"):

    options = {opt: config.get(section, opt)
               for opt in config.options(section)
               if opt.startswith("sqlalchemy.")}

    return engine_from_config(options)


def create_session(engine):

    session = scoped_session(sessionmaker())
    session.configure(bind=engine)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    return session


def add_default_data(session, data):

    for params in data:

        cls = 'aybu.core.models.%s' % params.pop('cls_')
        cls = get_object_from_python_path(cls)
        mapper = class_mapper(cls)

        for key, value in params.iteritems():

            if value is None:
                continue

            property_ = mapper.get_property(key)

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

        session.add(cls(**params))


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
