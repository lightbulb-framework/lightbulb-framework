# Copyright (C) 2017, Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import textwrap

from cliff import sphinxext
from cliff.tests import base


class TestSphinxExtension(base.TestBase):

    def test_empty_help(self):
        """Handle positional and optional actions without help messages."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', action='store')
        parser.add_argument('--language', dest='lang')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world [--language LANG] name

        .. option:: --language <LANG>

        .. option:: name
        """).lstrip(), output)

    def test_nonempty_help(self):
        """Handle positional and optional actions with help messages."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', help='user name')
        parser.add_argument('--language', dest='lang',
                            help='greeting language')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world [--language LANG] name

        .. option:: --language <LANG>

            greeting language

        .. option:: name

            user name
        """).lstrip(), output)

    def test_description_epilog(self):
        """Handle a parser description, epilog."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False,
                                         description='A "Hello, World" app.',
                                         epilog='What am I doing down here?')
        parser.add_argument('name', action='store')
        parser.add_argument('--language', dest='lang')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        A "Hello, World" app.

        .. program:: hello-world
        .. code-block:: shell

            hello-world [--language LANG] name

        .. option:: --language <LANG>

        .. option:: name

        What am I doing down here?
        """).lstrip(), output)

    def test_flag(self):
        """Handle a boolean argparse action."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', help='user name')
        parser.add_argument('--translate', action='store_true',
                            help='translate to local language')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world [--translate] name

        .. option:: --translate

            translate to local language

        .. option:: name

            user name
        """).lstrip(), output)

    def test_supressed(self):
        """Handle a supressed action."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', help='user name')
        parser.add_argument('--variable', help=argparse.SUPPRESS)

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world name


        .. option:: name

            user name
        """).lstrip(), output)

    def test_metavar(self):
        """Handle an option with a metavar."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('names', metavar='<NAME>', nargs='+',
                            help='a user name')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world <NAME> [<NAME> ...]

        .. option:: NAME

            a user name
        """).lstrip(), output)

    def test_multiple_opts(self):
        """Correctly output multiple opts on separate lines."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', help='user name')
        parser.add_argument('--language', dest='lang',
                            help='greeting language')
        parser.add_argument('--translate', action='store_true',
                            help='translate to local language')
        parser.add_argument('--write-to-var-log-something-or-other',
                            action='store_true',
                            help='a long opt to force wrapping')
        style_group = parser.add_mutually_exclusive_group(required=True)
        style_group.add_argument('--polite', action='store_true',
                                 help='use a polite greeting')
        style_group.add_argument('--profane', action='store_true',
                                 help='use a less polite greeting')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world
                [--language LANG]
                [--translate]
                [--write-to-var-log-something-or-other]
                (--polite | --profane)
                name

        .. option:: --language <LANG>

            greeting language

        .. option:: --translate

            translate to local language

        .. option:: --write-to-var-log-something-or-other

            a long opt to force wrapping

        .. option:: --polite

            use a polite greeting

        .. option:: --profane

            use a less polite greeting

        .. option:: name

            user name
        """).lstrip(), output)
