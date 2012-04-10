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
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


setup(name='aybu-core',
      version=':versiontools:aybu.core:',
      description='aybu-core',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Giacomo Bagnoli, Luca Frosini',
      author_email='g.bagnoli@asidev.com, l.frosini@asidev.com',
      url='https://code.asidev.net/projects/aybu',
      keywords='web pyramid pylons',
      namespace_packages=['aybu'],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=('pyramid<1.3a', 'SQLAlchemy<0.8a',
                        'Babel', 'PufferFish>=0.2', 'Wand',
                        'requests>=0.10', 'alembic',
                        'httpcachepurger', 'BeautifulSoup'),
      tests_require=('nose', 'coverage'),
      setup_requires=('versiontools >= 1.8',),
      test_suite="tests",
      message_extractors={
            'aybu.core': [
                ('**.py', 'python', None),
                ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
                ('static/**', 'ignore', None)]},
      entry_points="""\
      [paste.app_factory]
      main = aybu.core:main

      [paste.paster_command]
      uwsgi = pasteuwsgi.serve:ServeCommand
      aybu-setup = aybu.core.utils.command:SetupApp
      aybu-import = aybu.core.utils.command:Import
      aybu-export = aybu.core.utils.command:Export

      [nose.plugins.0.10]
      aybuconfig = aybu.core.testing:ReadAybuConfigPlugin

      """,
      paster_plugins=['pyramid'],
      )
