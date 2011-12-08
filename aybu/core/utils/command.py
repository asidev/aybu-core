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

from paste.script.command import BadCommand
from paste.script.command import Command
from paste.deploy.loadwsgi import appconfig
from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config
import json
import os
import pkg_resources

from aybu.core.models import (add_default_data,
                              init_session_events,
                              User,
                              Base,
                              Group)

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
