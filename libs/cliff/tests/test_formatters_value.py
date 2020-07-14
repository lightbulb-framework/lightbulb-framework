#!/usr/bin/env python
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

import six

from cliff.formatters import value
from cliff.tests import base
from cliff.tests import test_columns


class TestValueFormatter(base.TestBase):

    def test(self):
        sf = value.ValueFormatter()
        c = ('a', 'b', 'c', 'd')
        d = ('A', 'B', 'C', '"no escape me"')
        expected = 'A\nB\nC\n"no escape me"\n'
        output = six.StringIO()
        sf.emit_one(c, d, output, None)
        actual = output.getvalue()
        self.assertEqual(expected, actual)

    def test_formattable_column(self):
        sf = value.ValueFormatter()
        c = ('a', 'b', 'c', 'd')
        d = ('A', 'B', 'C', test_columns.FauxColumn(['the', 'value']))
        expected = "A\nB\nC\n['the', 'value']\n"
        output = six.StringIO()
        sf.emit_one(c, d, output, None)
        actual = output.getvalue()
        self.assertEqual(expected, actual)

    def test_list_formatter(self):
        sf = value.ValueFormatter()
        c = ('a', 'b', 'c')
        d1 = ('A', 'B', 'C')
        d2 = ('D', 'E', 'F')
        data = [d1, d2]
        expected = 'A B C\nD E F\n'
        output = six.StringIO()
        sf.emit_list(c, data, output, None)
        actual = output.getvalue()
        self.assertEqual(expected, actual)

    def test_list_formatter_formattable_column(self):
        sf = value.ValueFormatter()
        c = ('a', 'b', 'c')
        d1 = ('A', 'B', test_columns.FauxColumn(['the', 'value']))
        data = [d1]
        expected = "A B ['the', 'value']\n"
        output = six.StringIO()
        sf.emit_list(c, data, output, None)
        actual = output.getvalue()
        self.assertEqual(expected, actual)
