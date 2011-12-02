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
import ConfigParser
import os

from aybu.core.models import populate, init_session_events
from aybu.core.models import (engine_from_config_parser,
                              default_data_from_config,
                              create_session)


class SetupApp(Command):

    min_args = 0
    usage = 'CONFIG_FILE SECTION'
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

        if len(self.args) < 2:
            raise BadCommand('You must give a section name')

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        section_name = self.args[1]
        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name)

        config = ConfigParser.ConfigParser()
        config.read([file_name])
        engine = engine_from_config_parser(config, section_name)
        session = create_session(engine, True)
        init_session_events(session=session)
        data = default_data_from_config(config)
        populate(config, data, session)
        session.close()
