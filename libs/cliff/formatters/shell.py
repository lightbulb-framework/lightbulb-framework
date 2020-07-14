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

"""Output formatters using shell syntax.
"""

from . import base
from cliff import columns

import argparse
import six


class ShellFormatter(base.SingleFormatter):

    def add_argument_group(self, parser):
        group = parser.add_argument_group(
            title='shell formatter',
            description='a format a UNIX shell can parse (variable="value")',
        )
        group.add_argument(
            '--variable',
            action='append',
            default=[],
            dest='variables',
            metavar='VARIABLE',
            help=argparse.SUPPRESS,
        )
        group.add_argument(
            '--prefix',
            action='store',
            default='',
            dest='prefix',
            help='add a prefix to all variable names',
        )

    def emit_one(self, column_names, data, stdout, parsed_args):
        variable_names = [c.lower().replace(' ', '_')
                          for c in column_names
                          ]
        desired_columns = parsed_args.variables
        for name, value in zip(variable_names, data):
            if name in desired_columns or not desired_columns:
                value = (six.text_type(value.machine_readable())
                         if isinstance(value, columns.FormattableColumn)
                         else value)
                if isinstance(value, six.string_types):
                    value = value.replace('"', '\\"')
                if isinstance(name, six.string_types):
                    # Colons and dashes may appear as a resource property but
                    # are invalid to use in a shell, replace them with an
                    # underscore.
                    name = name.replace(':', '_')
                    name = name.replace('-', '_')
                stdout.write('%s%s="%s"\n' % (parsed_args.prefix, name, value))
        return
