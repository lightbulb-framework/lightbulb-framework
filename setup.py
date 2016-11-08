#!/usr/bin/env python
import ez_setup
import os
import imp
from sys import platform

ez_setup.use_setuptools()

PROJECT = 'lightbulb-framework'

# Change docs/sphinx/conf.py too!
VERSION = '0.0.2'

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
    install_requires=['cliff','symautomata','sfalearn', 'multiprocessing'],
    dependency_links=[
        "git+https://github.com/GeorgeArgyros/symautomata#egg=symautomata-0.0.2",
        "git+https://github.com/GeorgeArgyros/sfalearn#egg=sfalearn-0.0.2"
    ],
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

def check_for_MySQLdb():
    try:
        print 'Checking for MySQLdb module:',
        imp.find_module('MySQLdb')
        print 'OK'
    except ImportError:
        print 'FAIL'

        print 'It is recommended to use MySQLdb in order to support' \
              ' membership queries in mysql database'
        install = raw_input(
            ('* Install MySQLdb now? [y/n] ')
        )
        if install == 'y':
            if platform == "linux" or platform == "linux2":
                os.system('sudo apt-get install python-dev libmysqlclient-dev')
                os.system('pip install MySQL-python')
            elif platform == "darwin":
                os.system('[ ! -f "`which brew`" ] &&  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"')
                os.system('brew install mysql-connector-c')
                os.system('pip install MySQL-python')
            elif platform == "win32":
                print 'Automated installation is not supported for windows platform'

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

check_for_MySQLdb()
