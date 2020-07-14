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

import unittest

from cliff import columns


class FauxColumn(columns.FormattableColumn):

    def human_readable(self):
        return u'I made this string myself: {}'.format(self._value)


class TestColumns(unittest.TestCase):

    def test_faux_column_machine(self):
        c = FauxColumn(['list', 'of', 'values'])
        self.assertEqual(['list', 'of', 'values'], c.machine_readable())

    def test_faux_column_human(self):
        c = FauxColumn(['list', 'of', 'values'])
        self.assertEqual(
            u"I made this string myself: ['list', 'of', 'values']",
            c.human_readable(),
        )
