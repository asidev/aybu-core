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

from pyramid.util import DottedNameResolver
from paste.script.command import BadCommand
from paste.script.command import Command
import ConfigParser
import os


class SetupApp(Command):

    min_args = 0
    usage = 'CONFIG_FILE'
    takes_config_file = 1
    summary = "Run the described application setup routine."
    description = """\
    This command runs the setup routine of an application
    that uses a paste.deploy configuration file.
    """

    parser = Command.standard_parser(verbose=True)
    """
    parser.add_option('-n', '--app-name',
                      dest='app_name',
                      metavar='NAME',
                      help="Load the named application (default main)")
    parser.add_option("-u", "--dburi",
                      action="store",
                      dest="dburi",
                      default=None,
                      help="URI for database connection")
    """

    def command(self):

        if not self.args:
            raise BadCommand('You must give a configuration file.')

        """
        if not "VIRTUAL_ENV" in os.environ:
            raise BadCommand('You cannot run this command' +\
                             'outside a virtual enviroment.')

        if self.verbose:
            logging.basicConfig(level=logging.DEBUG)

        else:
            logging.basicConfig(level=logging.WARN)

        self.log = logging.getLogger(__name__)

        self.log.debug("Setting up database")
        """

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name)

        config = ConfigParser.ConfigParser()
        config.read([file_name])

        try:
            option = config.get('commands', 'setup-app')
            # Load a callable using 'setup-app' option as fully qualified name.
        except Exception:
            raise ValueError('Unable to find any command ' + \
                             'to setup the application ')

        setup_app = DottedNameResolver(None).resolve(option)
        setup_app(config)
