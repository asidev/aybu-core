#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['pyramid',
            'SQLAlchemy',
            'Mako']

setup(name='aybu-core',
      version='0.2.0a1',
      description='aybu-core',
      long_description=README + '\n\n' +  CHANGES,
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
      install_requires=requires,
      tests_require=requires,
      test_suite="tests",
      message_extractors = {
            'aybu.core': [
                ('**.py', 'python', None),
                ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
                ('static/**', 'ignore', None)
            ],
            'aybu.themes': [
                ('*/templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
                ('*/static/**', 'ignore', None)

            ]
      },
      entry_points = """\
      [paste.app_factory]
      main = aybu.core:main

      [paste.paster_command]
      uwsgi = pasteuwsgi.serve:ServeCommand
      """,
      paster_plugins=['pyramid'],
      )
