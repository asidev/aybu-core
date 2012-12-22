#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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
                              File,
                              Image,
                              Banner,
                              Logo)
from aybu.core.utils.archive import import_
from aybu.core.utils.archive import export

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
            msg = 'You must give a configuration file and an archive name.'
            raise BadCommand(msg)

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        archive_name = self.args[1]
        if not archive_name.startswith("/"):
            archive_name = os.path.join(os.getcwd(), archive_name)

        if not archive_name.endswith(".tar.gz"):
            archive_name = '{}.tar.gz'.format(archive_name)

        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name.split('#')[0])

        config = appconfig('config:{}'.format(file_name))
        engine = engine_from_config(config, 'sqlalchemy.')
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()
        src = pkg_resources.resource_filename('aybu.instances.%s' % config['instance'],
                                              'static')
        log.info('Using %s for static files', src)
        instance_static_path = os.path.realpath(src)
        upload_path = os.path.join(instance_static_path, 'uploads')
        file_base = os.path.join(upload_path, "files")
        image_base = os.path.join(upload_path, "images")
        banner_base = os.path.join(upload_path, "banners")
        logo_base = os.path.join(upload_path, "logo")
        prefix = 'static'
        File.initialize(base=file_base,
                        private=instance_static_path,
                        url_prefix=prefix)
        Image.initialize(base=image_base,
                         private=instance_static_path,
                         url_prefix=prefix)
        Banner.initialize(base=banner_base,
                          private=instance_static_path,
                          url_prefix=prefix)
        Logo.initialize(base=logo_base,
                        private=instance_static_path,
                        url_prefix=prefix)
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
            for obj in data:
                if obj['__class__'] in ('File', 'Image', 'Banner', 'Logo'):
                    file_ = open(os.path.join(base_path, obj['source']))
                    obj['source'] = file_.read()
                    file_.close()
            import_(session, data)

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
    summary = "Export data and files."
    description = """\
    This command extracts data and files from the database
    and saves them in an archive.
    """

    parser = Command.standard_parser(verbose=True)

    def command(self):

        if not self.args or len(self.args) < 2:
            msg = 'You must give a configuration file and an archive name.'
            raise BadCommand(msg)

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        archive_name = self.args[1]
        if not archive_name.startswith("/"):
            archive_name = os.path.join(os.getcwd(), archive_name)

        if not archive_name.endswith(".tar.gz"):
            archive_name = '{}.tar.gz'.format(archive_name)

        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name.split('#')[0])

        config = appconfig('config:{}'.format(file_name))
        engine = engine_from_config(config, 'sqlalchemy.')
        Base.metadata.bind = engine
        Base.metadata.create_all()
        src = pkg_resources.resource_filename('aybu.instances.%s' % config['instance'],
                                              'static')
        log.info('Using %s for static files', src)
        instance_static_path = os.path.realpath(src)
        upload_path = os.path.join(instance_static_path, 'uploads')
        file_base = os.path.join(upload_path, "files")
        image_base = os.path.join(upload_path, "images")
        banner_base = os.path.join(upload_path, "banners")
        logo_base = os.path.join(upload_path, "logo")
        prefix = 'static'
        File.initialize(base=file_base, private=instance_static_path,
                            url_prefix=prefix)
        Image.initialize(base=image_base, private=instance_static_path,
                             url_prefix=prefix)
        Banner.initialize(base=banner_base, private=instance_static_path,
                              url_prefix=prefix)
        Logo.initialize(base=logo_base, private=instance_static_path,
                            url_prefix=prefix)
        Session = sessionmaker(bind=engine)
        session = Session()
        init_session_events(session)
        tar = tarfile.open(archive_name, 'w:gz')
        try:
            data = export(session)
            for obj in data:
                if obj['__class__'] in ('File', 'Image', 'Banner', 'Logo'):
                    arcname = '{}/{}'.format(obj['id'], obj['name'])
                    tar.add(obj['source'], arcname=arcname)
                    obj['source'] = arcname

            filename = 'data.json'
            with open(filename, 'w') as file_:
                data = json.dumps(data, encoding='utf-8')
                print data
                file_.write(data)
            tar.add(filename)
            os.remove(filename)

        except Exception as e:
            log.exception('Cannot export data from database.')
            session.rollback()
            raise e

        finally:
            session.close()
            tar.close()
