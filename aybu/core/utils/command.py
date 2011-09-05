#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

"""Setup the aybu application"""

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

        except Exception as e:

            raise ValueError('Unable to find any command ' + \
                             'to setup the application ')

        setup_app = DottedNameResolver(None).resolve(option)
        setup_app(config)
