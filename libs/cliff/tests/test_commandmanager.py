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

import mock
import testscenarios

from cliff import commandmanager
from cliff.tests import base
from cliff.tests import utils


load_tests = testscenarios.load_tests_apply_scenarios


class TestLookupAndFind(base.TestBase):

    scenarios = [
        ('one-word', {'argv': ['one']}),
        ('two-words', {'argv': ['two', 'words']}),
        ('three-words', {'argv': ['three', 'word', 'command']}),
    ]

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        cmd, name, remaining = mgr.find_command(self.argv)
        self.assertTrue(cmd)
        self.assertEqual(' '.join(self.argv), name)
        self.assertFalse(remaining)


class TestLookupWithRemainder(base.TestBase):

    scenarios = [
        ('one', {'argv': ['one', '--opt']}),
        ('two', {'argv': ['two', 'words', '--opt']}),
        ('three', {'argv': ['three', 'word', 'command', '--opt']}),
    ]

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        cmd, name, remaining = mgr.find_command(self.argv)
        self.assertTrue(cmd)
        self.assertEqual(['--opt'], remaining)


class TestFindInvalidCommand(base.TestBase):

    scenarios = [
        ('no-such-command', {'argv': ['a', '-b']}),
        ('no-command-given', {'argv': ['-b']}),
    ]

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        try:
            mgr.find_command(self.argv)
        except ValueError as err:
            # make sure err include 'a' when ['a', '-b']
            self.assertIn(self.argv[0], str(err))
            self.assertIn('-b', str(err))
        else:
            self.fail('expected a failure')


class TestFindUnknownCommand(base.TestBase):

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        try:
            mgr.find_command(['a', 'b'])
        except ValueError as err:
            self.assertIn("['a', 'b']", str(err))
        else:
            self.fail('expected a failure')


class TestDynamicCommands(base.TestBase):

    def test_add(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mock_cmd = mock.Mock()
        mgr.add_command('mock', mock_cmd)
        found_cmd, name, args = mgr.find_command(['mock'])
        self.assertIs(mock_cmd, found_cmd)

    def test_intersected_commands(self):
        def foo(arg):
            pass

        def foo_bar():
            pass

        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mgr.add_command('foo', foo)
        mgr.add_command('foo bar', foo_bar)

        self.assertIs(foo_bar, mgr.find_command(['foo', 'bar'])[0])
        self.assertIs(
            foo,
            mgr.find_command(['foo', 'arg0'])[0],
        )


class TestLoad(base.TestBase):

    def test_load_commands(self):
        testcmd = mock.Mock(name='testcmd')
        testcmd.name.replace.return_value = 'test'
        mock_pkg_resources = mock.Mock(return_value=[testcmd])
        with mock.patch('pkg_resources.iter_entry_points',
                        mock_pkg_resources) as iter_entry_points:
            mgr = commandmanager.CommandManager('test')
            iter_entry_points.assert_called_once_with('test')
            names = [n for n, v in mgr]
            self.assertEqual(['test'], names)

    def test_load_commands_keep_underscores(self):
        testcmd = mock.Mock()
        testcmd.name = 'test_cmd'
        mock_pkg_resources = mock.Mock(return_value=[testcmd])
        with mock.patch('pkg_resources.iter_entry_points',
                        mock_pkg_resources) as iter_entry_points:
            mgr = commandmanager.CommandManager(
                'test',
                convert_underscores=False,
            )
            iter_entry_points.assert_called_once_with('test')
            names = [n for n, v in mgr]
            self.assertEqual(['test_cmd'], names)

    def test_load_commands_replace_underscores(self):
        testcmd = mock.Mock()
        testcmd.name = 'test_cmd'
        mock_pkg_resources = mock.Mock(return_value=[testcmd])
        with mock.patch('pkg_resources.iter_entry_points',
                        mock_pkg_resources) as iter_entry_points:
            mgr = commandmanager.CommandManager(
                'test',
                convert_underscores=True,
            )
            iter_entry_points.assert_called_once_with('test')
            names = [n for n, v in mgr]
            self.assertEqual(['test cmd'], names)
