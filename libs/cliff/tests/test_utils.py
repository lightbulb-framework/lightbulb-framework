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

import os
import struct
import sys
import unittest

import mock

from cliff import utils
from cliff.tests import base


class TestTerminalWidth(base.TestBase):

    def test(self):
        width = utils.terminal_width(sys.stdout)
        # Results are specific to the execution environment, so only assert
        # that no error is raised.
        if width is not None:
            self.assertIsInstance(width, int)

    @unittest.skipIf(not hasattr(os, 'get_terminal_size'),
                     'only needed for python 3.3 onwards')
    @mock.patch('cliff.utils.os')
    def test_get_terminal_size(self, mock_os):
        ts = os.terminal_size((10, 5))
        mock_os.get_terminal_size.return_value = ts
        width = utils.terminal_width(sys.stdout)
        self.assertEqual(10, width)
        mock_os.get_terminal_size.side_effect = OSError()
        width = utils.terminal_width(sys.stdout)
        self.assertIs(None, width)

    @unittest.skipIf(hasattr(os, 'get_terminal_size'),
                     'only needed for python 3.2 and before')
    @mock.patch('fcntl.ioctl')
    def test_ioctl(self, mock_ioctl):
        mock_ioctl.return_value = struct.pack('hhhh', 57, 101, 0, 0)
        width = utils.terminal_width(sys.stdout)
        self.assertEqual(101, width)
        mock_ioctl.side_effect = IOError()
        width = utils.terminal_width(sys.stdout)
        self.assertIs(None, width)

    @unittest.skipIf(hasattr(os, 'get_terminal_size'),
                     'only needed for python 3.2 and before')
    @mock.patch('cliff.utils.ctypes')
    @mock.patch('sys.platform', 'win32')
    def test_windows(self, mock_ctypes):
        mock_ctypes.create_string_buffer.return_value.raw = struct.pack(
            'hhhhHhhhhhh', 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        mock_ctypes.windll.kernel32.GetStdHandle.return_value = -11
        mock_ctypes.windll.kernel32.GetConsoleScreenBufferInfo.return_value = 1

        width = utils.terminal_width(sys.stdout)
        self.assertEqual(101, width)

        mock_ctypes.windll.kernel32.GetConsoleScreenBufferInfo.return_value = 0

        width = utils.terminal_width(sys.stdout)
        self.assertIs(None, width)

        width = utils.terminal_width('foo')
        self.assertIs(None, width)
