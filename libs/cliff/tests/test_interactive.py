# -*- encoding: utf-8 -*-
#
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

import cmd2

from cliff.interactive import InteractiveApp
from cliff.tests import base


class FakeApp(object):
    NAME = 'Fake'


class TestInteractive(base.TestBase):

    def make_interactive_app(self, *command_names):
        fake_command_manager = [(x, None) for x in command_names]
        return InteractiveApp(FakeApp, fake_command_manager,
                              stdin=None, stdout=None)

    def _test_completenames(self, expecteds, prefix):
        app = self.make_interactive_app('hips', 'hippo', 'nonmatching')
        self.assertEqual(
            set(app.completenames(prefix, '', 0, 1)), set(expecteds))

    def test_cmd2_completenames(self):
        # cmd2.Cmd define do_help method
        self._test_completenames(['help'], 'he')

    def test_cliff_completenames(self):
        self._test_completenames(['hips', 'hippo'], 'hip')

    def test_no_completenames(self):
        self._test_completenames([], 'taz')

    def test_both_completenames(self):
        # cmd2.Cmd define do_history method
        # NOTE(dtroyer): Before release 0.7.0 do_hi was also defined so we need
        #                to account for that in the list of possible responses.
        #                Remove this check after cmd2 0.7.0 is the minimum
        #                requirement.
        if hasattr(cmd2.Cmd, "do_hi"):
            self._test_completenames(['hi', 'history', 'hips', 'hippo'], 'hi')
        else:
            self._test_completenames(['history', 'hips', 'hippo'], 'hi')

    def _test_completedefault(self, expecteds, line, begidx):
        command_names = set(['show file', 'show folder', 'show  long',
                             'list all'])
        app = self.make_interactive_app(*command_names)
        observeds = app.completedefault(None, line, begidx, None)
        self.assertEqual(set(expecteds), set(observeds))
        self.assertTrue(
            set([line[:begidx] + x for x in observeds]) <= command_names
        )

    def test_empty_text_completedefault(self):
        # line = 'show ' + begidx = 5 implies text = ''
        self._test_completedefault(['file', 'folder', ' long'], 'show ', 5)

    def test_nonempty_text_completedefault2(self):
        # line = 'show f' + begidx = 6 implies text = 'f'
        self._test_completedefault(['file', 'folder'], 'show f', 5)

    def test_long_completedefault(self):
        self._test_completedefault(['long'], 'show  ', 6)

    def test_no_completedefault(self):
        self._test_completedefault([], 'taz ', 4)
