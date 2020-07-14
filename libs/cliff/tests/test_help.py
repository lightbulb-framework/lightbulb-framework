#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

try:
    from StringIO import StringIO
except:
    from io import StringIO
import os
import sys

import mock

from cliff import app as application
from cliff import commandmanager
from cliff import help
from cliff.tests import base
from cliff.tests import utils


class TestHelp(base.TestBase):

    def test_show_help_for_command(self):
        # FIXME(dhellmann): Are commands tied too closely to the app? Or
        # do commands know too much about apps by using them to get to the
        # command manager?
        stdout = StringIO()
        app = application.App('testing', '1',
                              utils.TestCommandManager(utils.TEST_NAMESPACE),
                              stdout=stdout)
        app.NAME = 'test'
        help_cmd = help.HelpCommand(app, mock.Mock())
        parser = help_cmd.get_parser('test')
        parsed_args = parser.parse_args(['one'])
        try:
            help_cmd.run(parsed_args)
        except SystemExit:
            pass
        self.assertEqual('TestParser', stdout.getvalue())

    def test_list_matching_commands(self):
        # FIXME(dhellmann): Are commands tied too closely to the app? Or
        # do commands know too much about apps by using them to get to the
        # command manager?
        stdout = StringIO()
        app = application.App('testing', '1',
                              utils.TestCommandManager(utils.TEST_NAMESPACE),
                              stdout=stdout)
        app.NAME = 'test'
        help_cmd = help.HelpCommand(app, mock.Mock())
        parser = help_cmd.get_parser('test')
        parsed_args = parser.parse_args(['t'])
        try:
            help_cmd.run(parsed_args)
        except SystemExit:
            pass
        help_output = stdout.getvalue()
        self.assertIn('Command "t" matches:', help_output)
        self.assertIn('three word command\n  two words\n', help_output)

    def test_list_matching_commands_no_match(self):
        # FIXME(dhellmann): Are commands tied too closely to the app? Or
        # do commands know too much about apps by using them to get to the
        # command manager?
        stdout = StringIO()
        app = application.App('testing', '1',
                              utils.TestCommandManager(utils.TEST_NAMESPACE),
                              stdout=stdout)
        app.NAME = 'test'
        help_cmd = help.HelpCommand(app, mock.Mock())
        parser = help_cmd.get_parser('test')
        parsed_args = parser.parse_args(['z'])
        self.assertRaises(
            ValueError,
            help_cmd.run,
            parsed_args,
        )

    def test_show_help_for_help(self):
        # FIXME(dhellmann): Are commands tied too closely to the app? Or
        # do commands know too much about apps by using them to get to the
        # command manager?
        stdout = StringIO()
        app = application.App('testing', '1',
                              utils.TestCommandManager(utils.TEST_NAMESPACE),
                              stdout=stdout)
        app.NAME = 'test'
        app.options = mock.Mock()
        help_cmd = help.HelpCommand(app, mock.Mock())
        parser = help_cmd.get_parser('test')
        parsed_args = parser.parse_args([])
        try:
            help_cmd.run(parsed_args)
        except SystemExit:
            pass
        help_text = stdout.getvalue()
        basecommand = os.path.split(sys.argv[0])[1]
        self.assertIn('usage: %s [--version]' % basecommand, help_text)
        self.assertIn('optional arguments:\n  --version', help_text)
        expected = (
            '  one            Test command.\n'
            '  three word command  Test command.\n'
        )
        self.assertIn(expected, help_text)

    def test_list_deprecated_commands(self):
        # FIXME(dhellmann): Are commands tied too closely to the app? Or
        # do commands know too much about apps by using them to get to the
        # command manager?
        stdout = StringIO()
        app = application.App('testing', '1',
                              utils.TestCommandManager(utils.TEST_NAMESPACE),
                              stdout=stdout)
        app.NAME = 'test'
        try:
            app.run(['--help'])
        except SystemExit:
            pass
        help_output = stdout.getvalue()
        self.assertIn('two words', help_output)
        self.assertIn('three word command', help_output)
        self.assertNotIn('old cmd', help_output)

    @mock.patch.object(commandmanager.EntryPointWrapper, 'load',
                       side_effect=Exception('Could not load EntryPoint'))
    def test_show_help_with_ep_load_fail(self, mock_load):
        stdout = StringIO()
        app = application.App('testing', '1',
                              utils.TestCommandManager(utils.TEST_NAMESPACE),
                              stdout=stdout)
        app.NAME = 'test'
        app.options = mock.Mock()
        app.options.debug = False
        help_cmd = help.HelpCommand(app, mock.Mock())
        parser = help_cmd.get_parser('test')
        parsed_args = parser.parse_args([])
        try:
            help_cmd.run(parsed_args)
        except SystemExit:
            pass
        help_output = stdout.getvalue()
        self.assertIn('Commands:', help_output)
        self.assertIn('Could not load', help_output)
        self.assertNotIn('Exception: Could not load EntryPoint', help_output)

    @mock.patch.object(commandmanager.EntryPointWrapper, 'load',
                       side_effect=Exception('Could not load EntryPoint'))
    def test_show_help_print_exc_with_ep_load_fail(self, mock_load):
        stdout = StringIO()
        app = application.App('testing', '1',
                              utils.TestCommandManager(utils.TEST_NAMESPACE),
                              stdout=stdout)
        app.NAME = 'test'
        app.options = mock.Mock()
        app.options.debug = True
        help_cmd = help.HelpCommand(app, mock.Mock())
        parser = help_cmd.get_parser('test')
        parsed_args = parser.parse_args([])
        try:
            help_cmd.run(parsed_args)
        except SystemExit:
            pass
        help_output = stdout.getvalue()
        self.assertIn('Commands:', help_output)
        self.assertIn('Could not load', help_output)
        self.assertIn('Exception: Could not load EntryPoint', help_output)
