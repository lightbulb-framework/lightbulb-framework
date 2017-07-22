#!/usr/bin/env python
import ez_setup
import os
import imp
from sys import platform

ez_setup.use_setuptools()

PROJECT = 'lightbulb-framework'

# Change docs/sphinx/conf.py too!
VERSION = '0.0.17'

from setuptools import setup, find_packages

try:
    long_description = open('README.md', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Tools for auditing WAFS',
    long_description=long_description,

    author='George Argyros, Ioannis Stais',
    author_email='ioannis.stais@gmail.com',

    url='https://github.com/lightbulb-framework/lightbulb-framework',
    download_url='https://github.com/lightbulb-framework/lightbulb-framework/tarball/master',

    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Environment :: Console',
                 ],

    platforms=['Any'],
    scripts=[],
    provides=[],
    install_requires=['six>=1.10', 'stevedore', 'pbr', 'cmd2', 'unicodecsv', 'pyYAML', 'PrettyTable', 'cliff', 'multiprocessing', 'symautomata>=0.0.11', 'sfalearn>=0.0.9'],
    dependency_links=[],
    namespace_packages=[],
    packages=[ "lightbulb"]+find_packages(),
    package_data={
          'lightbulb-framework': ['data/*'],
       },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'lightbulb = lightbulb.lightbulb:main'
        ],
        'cliff.lightbulb': [
            'start =  lightbulb.cli.use:StartSaved',
            'modules = lightbulb.cli.show:Modules',
            'core = lightbulb.cli.show:Core',
            'utils = lightbulb.cli.show:Utils',
            'info = lightbulb.cli.show:Info',
            'use = lightbulb.cli.use:Use',
            'library = lightbulb.cli.use:Library',
            'status = lightbulb.cli.use:Status',
        ],
        'cliff.modulehandler': [
            'start =  lightbulb.cli.use:Start',
            'info = lightbulb.cli.use:Info',
            'options = lightbulb.cli.use:Options',
            'define = lightbulb.cli.use:Define',
            'back = lightbulb.cli.use:Back',
            'library = lightbulb.cli.use:Library',
        ],
        'cliff.libraryhandler': [
            'back = lightbulb.cli.use:LibraryBack',
            'info = lightbulb.cli.show:LibraryInfo',
            'cat = lightbulb.cli.show:LibraryCat',
            'modules = lightbulb.cli.show:LibraryModules',
            'search = lightbulb.cli.show:LibrarySearch',
        ],
        'setuptools.installation': [
            'lightbulb = lightbulb.lightbulb:main',
        ]
    },
    zip_safe=False,
)

