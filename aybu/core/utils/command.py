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

import logging
from alembic.config import Config
from alembic import command
from paste.script.command import BadCommand
from paste.script.command import Command
from paste.deploy.loadwsgi import appconfig
from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config
import json
import os
import pkg_resources
import tempfile
import tarfile
import shutil

from aybu.core.models import (add_default_data,
                              init_session_events,
                              User,
                              Base,
                              Group,
                              Language,
                              View,
                              ViewDescription,
                              __entities__,
                              import_,
                              CommonInfo,
                              PageInfo)

log = logging.getLogger(__name__)


class SetupApp(Command):

    min_args = 0
    usage = 'CONFIG_FILE[#section]'
    takes_config_file = 1
    summary = "Run the described application setup routine."
    description = """\
    This command runs the setup routine of an application
    that uses a paste.deploy configuration file.
    """

    parser = Command.standard_parser(verbose=True)

    def command(self):

        if not self.args:
            raise BadCommand('You must give a configuration file.')

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name)

        config = appconfig('config:{}'.format(file_name))
        engine = engine_from_config(config, 'sqlalchemy.')
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()
        command.stamp(Config(file_name.split('#')[0]), 'head')
        Session = sessionmaker(bind=engine)
        try:
            session = Session()
            init_session_events(session)
            source_ = pkg_resources.resource_stream('aybu.core.data',
                                                    'default_data.json')
            data = json.loads(source_.read())

            add_default_data(session, data)
            user = User(username=config['default_user.username'],
                        password=config['default_user.password'])
            session.merge(user)
            group = Group(name=u'admin')
            group.users.append(user)
            session.merge(group)
            session.flush()

        except:
            session.rollback()

        else:
            session.commit()

        finally:
            session.close()
            source_.close()


class Convert(Command):

    min_args = 1
    usage = 'TAR_FILE'
    takes_config_file = 0
    summary = "Convert the old AYBU 1.0 TAR file format in the new one."
    description = """\
    This command convert the old AYBU 1.0 TAR file format and data
    in the new one that is used by AYBU 2.0 restore function.
    """

    parser = Command.standard_parser(verbose=True)

    def command(self):

        if not self.args:
            msg = 'You must give the archive file path.'
            raise BadCommand(msg)

        file_name = self.args[0]

        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        base_path = tempfile.mkdtemp()
        tar = tarfile.open(file_name, 'r')
        tar.extractall(path=base_path)
        tar.close()
        json_data = os.path.join(base_path, 'data.json')
        data = open(json_data, 'r')
        data = json.load(data, encoding='utf-8')
        banner = None
        logo = None
        file_max_id = 0

        # Import SettingsType from aybu.core default data.
        # We ignore SettingTypes from the aybu1.0 data.
        default_data = json.load(
                            pkg_resources.resource_stream('aybu.core.data',
                                                          'default_data.json'))

        data['SettingType'] = [
            dict(name=d['name'], raw_type=d['raw_type'])
            for d in default_data if d['cls_'] == "SettingType"
        ]

        # Change Setting structure.
        for setting in data['Setting']:
            if setting['name'] == 'theme_name':
                setting['value'] = setting['value'].replace("-", "_")

            if setting['name'] == 'banner':
                banner = setting['value']

            elif setting['name'] == 'logo':
                logo = setting['value']

            # Remove the key 'raw_type'.
            old_raw_type = setting.pop('raw_type')
            old_type_name = setting.pop('type_name')

            # Add the key 'raw_value'
            setting['raw_value'] = setting.pop('value')
            # Change SettingType structure
            if old_raw_type == 'int':
                setting['type_name'] = 'integer'

            elif old_raw_type == 'bool':
                setting['type_name'] = 'checkbox'

            elif old_raw_type == 'str':
                setting['type_name'] = 'string'

            elif old_raw_type == 'unicode':
                if setting['name'].startswith('contact_dst_email'):
                    setting['type_name'] = 'email'

                elif old_type_name in ('image', 'txt', 'html'):
                    setting['type_name'] = old_type_name

                else:
                    raise TypeError('Unknow setting type name {}'\
                                    .format(old_type_name))

            else:
                raise TypeError("Unknow raw type {}".format(old_raw_type))

        for entity in __entities__:
            entity = entity.__name__
            if entity not in data:
                print 'No %s entities in data file.' % entity
                continue

            entity_data = data[entity]
            for item in entity_data:
                item.pop('row_type', None)
                if entity == 'SettingType' and 'raw_type' not in item:
                    # FIXME: replace print with logging.
                    print 'Unused SettingType: set raw_type to Unicode.'
                    print item
                    item['raw_type'] = u'unicode'
                    continue

                elif entity == 'Setting':
                    continue

                elif entity == 'Theme':
                    item['name'] = item['name'].replace("-", "_")
                    if item['parent_name']:
                        item['parent_name'] = item['parent_name']\
                                                        .replace("-", "_")
                    continue

                elif entity in ('File', 'Image', 'Banner', 'Logo'):
                    item.pop('size')
                    item.pop('content_type')
                    item.pop('url')
                    if int(item['id']) > file_max_id:
                        file_max_id = int(item['id'])
                    continue

                elif entity == 'Node':
                    item_entity = item['__class__']

                elif entity == 'NodeInfo':
                    item_entity = item['__class__']

                else:
                    continue

                if item_entity == 'Menu':
                    item.pop('home')
                    item.pop('sitemap_priority')
                    item.pop('view_id')
                    item.pop('linked_to_id')
                    item.pop('url')
                    item.pop('banners')

                elif item_entity == 'MenuInfo':
                    if item['node_id'] == 1:
                        item['label'] = "Menù Principale"
                    else:
                        item['label'] = 'Pagine Orfane'

                    item.pop('title')
                    item.pop('url_part')
                    item.pop('keywords')
                    item.pop('meta_description')
                    item.pop('head_content')
                    item.pop('content')
                    item.pop('files')
                    item.pop('images')
                    item.pop('links')

                elif item_entity == 'Section':
                    item.pop('home')
                    item.pop('sitemap_priority')
                    item.pop('view_id')
                    item.pop('linked_to_id')
                    item.pop('url')
                    item.pop('banners')

                elif item_entity == 'SectionInfo':
                    item.pop('meta_description')
                    item.pop('head_content')
                    item.pop('content')
                    item.pop('keywords')
                    item.pop('files')
                    item.pop('images')
                    item.pop('links')

                elif item_entity == 'Page':
                    item.pop('linked_to_id')
                    item.pop('url')

                elif item_entity == 'PageInfo':
                    item.pop('keywords')
                    item.pop('files')
                    item.pop('images')
                    item.pop('links')

                elif item_entity == 'ExternalLink':
                    item.pop('home')
                    item.pop('sitemap_priority')
                    item.pop('view_id')
                    item.pop('linked_to_id')
                    item.pop('banners')
                    item.pop('url')

                elif item_entity == 'ExternalLinkInfo':
                    item.pop('title')
                    item.pop('url_part')
                    item.pop('keywords')
                    item.pop('meta_description')
                    item.pop('head_content')
                    item.pop('content')
                    item.pop('files')
                    item.pop('images')
                    item.pop('links')

                elif item_entity == 'InternalLink':
                    item.pop('home')
                    item.pop('sitemap_priority')
                    item.pop('view_id')
                    item.pop('url')
                    item.pop('banners')

                elif item_entity == 'InternalLinkInfo':
                    item.pop('title')
                    item.pop('url_part')
                    item.pop('keywords')
                    item.pop('meta_description')
                    item.pop('head_content')
                    item.pop('content')
                    item.pop('files')
                    item.pop('images')
                    item.pop('links')

        logo_tmp_path = os.path.join(base_path,
                                     'static',
                                     'uploads',
                                     'images',
                                     logo)
        logo_path = os.path.join('static',
                                 'uploads',
                                 'images',
                                 logo)
        if os.path.exists(logo_tmp_path):
            if 'Logo' not in data:
                data['Logo'] = []
            data['Logo'].append(dict(id=file_max_id + 1,
                                     name=logo,
                                     path=logo_path,
                                     default=True))
            file_max_id = file_max_id + 1

        else:
            print 'NO LOGO!!!'

        banner_tmp_path = os.path.join(base_path,
                                       'static',
                                       'uploads',
                                       'images',
                                       banner)
        banner_path = os.path.join('static',
                                   'uploads',
                                   'images',
                                   banner)
        if os.path.exists(banner_tmp_path):
            if 'Banner' not in data:
                data['Banner'] = []
            data['Banner'].append(dict(id=file_max_id + 1,
                                       name=banner,
                                       path=banner_path,
                                       default=True))
            file_max_id = file_max_id + 1
        else:
            print 'NO DEFAULT BANNER!!!'

        tar = tarfile.open(file_name, 'w:gz')
        tar.add(os.path.join(base_path, 'static'), 'static')
        json.dump(data, open(json_data, 'w'), encoding='utf-8')
        tar.add(json_data, 'data.json')
        shutil.rmtree(base_path)


class Import(Command):

    min_args = 2
    usage = 'CONFIG_FILE ARCHIVE'
    takes_config_file = 1
    summary = "Import data and file."
    description = """\
    This command extracts data and file from the archive
    to import them into the database.
    """

    parser = Command.standard_parser(verbose=True)

    def command(self):

        if not self.args or len(self.args) < 2:
            msg = 'You must give a configuration file and an archive.'
            raise BadCommand(msg)

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        archive_name = self.args[1]
        if not archive_name.startswith("/"):
            archive_name = os.path.join(os.getcwd(), archive_name)

        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name.split('#')[0])

        config = appconfig('config:{}'.format(file_name))
        engine = engine_from_config(config, 'sqlalchemy.')
        dst = pkg_resources.resource_filename('aybu.instances.{}'\
                                               .format(config['instance']),
                                               "static")
        log.info('Using %s for static files', dst)
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        base = os.path.join(dst, 'uploads')
        for dir_ in ['banners', 'images', 'files', 'logo']:
            dir_ = os.path.join(base, dir_)
            if os.path.exists(dir_):
                shutil.rmtree(dir_)
            os.makedirs(dir_)
        Base.metadata.create_all()
        Session = sessionmaker(bind=engine)
        session = Session()
        init_session_events(session)
        base_path = tempfile.mkdtemp()
        tar = tarfile.open(archive_name, 'r')
        tar.extractall(path=base_path)
        tar.close()
        json_data = os.path.join(base_path, 'data.json')
        data = json.load(open(json_data, 'r'), encoding='utf-8')
        try:
            import_(unicode(engine.url), session, data, base_path, dst)
            for info in session.query(PageInfo).all():
                info.update_associations()
            # add default users
            if config.get('default_user.username') and \
               config.get('default_user.password'):
                user = User(username=config['default_user.username'],
                            password=config['default_user.password'])
                session.add(user)
                group = Group(name=u'admin')
                group.users.append(user)
                session.add(group)
                session.flush()

            default_data = json.load(
                    pkg_resources.resource_stream('aybu.core.data',
                                                  'default_data.json')
            )

            # add View and ViewDescription for Media Collections
            mview_data = [v for v in default_data
                          if v['cls_'] == 'View'
                          and v['name'].startswith('MEDIA')][0]
            def_id = mview_data.pop('id')
            cls_ = mview_data.pop('cls_')
            mview = View(**mview_data)
            session.add(mview)
            session.flush()  # assign id to view.

            # readd cls_ to avoid keyerrors
            mview_data['cls_'] = cls_
            italian = [d for d in default_data
                      if d['cls_'] == 'Language' and d['lang'] == 'it'][0]

            mv_descr_data = [d for d in default_data
                             if d['cls_'] == 'ViewDescription'
                             and d['view'] == def_id
                             and d['language'] == italian['id']][0]
            mv_descr_data.pop('id')
            mv_descr_data.pop('cls_')
            mv_descr_data['view'] = mview
            mv_descr_data['language'] = Language.get_by_lang(session, 'it')

            session.add(ViewDescription(**mv_descr_data))
            session.flush()

        except Exception as e:
            log.exception('Error in import')
            session.rollback()
            raise e

        else:
            session.commit()

        finally:
            session.close()
            shutil.rmtree(base_path)


class Export(Command):

    min_args = 2
    usage = 'CONFIG_FILE ARCHIVE'
    takes_config_file = 1
    summary = "Import data and file."
    description = """\
    This command extracts data and file from the archive
    to import them into the database.
    """

    parser = Command.standard_parser(verbose=True)

    def command(self):

        if not self.args or len(self.args) < 2:
            raise BadCommand('You must give a configuration file and an archive.')

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        archive_name = self.args[1]
        if not archive_name.startswith("/"):
            archive_name = os.path.join(os.getcwd(), archive_name)

        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name)

        config = appconfig('config:{}'.format(file_name))
        engine = engine_from_config(config, 'sqlalchemy.')
        Base.metadata.bind = engine
        Base.metadata.create_all()
        Session = sessionmaker(bind=engine)
        try:
            session = Session()
            init_session_events(session)
            base_path = tempfile.mkdtemp()
            tar = tarfile.open(archive_name, 'r')
            tar.extractall(path=base_path)
            tar.close()
            json_data = os.path.join(base_path, 'data.json')
            data = json.load(open(json_data, 'r'))
            import_(data, os.path.join(base_path, 'static', 'uploads'))

        except:
            session.rollback()

        else:
            session.commit()

        finally:
            session.close()
            shutil.rmtree(base_path)
