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

import testtools

import fixtures


class TestBase(testtools.TestCase):

    def setUp(self):
        super(TestBase, self).setUp()
        self._stdout_fixture = fixtures.StringStream('stdout')
        self.stdout = self.useFixture(self._stdout_fixture).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        self._stderr_fixture = fixtures.StringStream('stderr')
        self.stderr = self.useFixture(self._stderr_fixture).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', self.stderr))
