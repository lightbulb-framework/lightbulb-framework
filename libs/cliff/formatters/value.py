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

"""Output formatters values only
"""

import six

from . import base
from cliff import columns


class ValueFormatter(base.ListFormatter, base.SingleFormatter):

    def add_argument_group(self, parser):
        pass

    def emit_list(self, column_names, data, stdout, parsed_args):
        for row in data:
            stdout.write(
                ' '.join(
                    six.text_type(c.machine_readable()
                                  if isinstance(c, columns.FormattableColumn)
                                  else c)
                    for c in row) + u'\n')
        return

    def emit_one(self, column_names, data, stdout, parsed_args):
        for value in data:
            stdout.write('%s\n' % six.text_type(
                value.machine_readable()
                if isinstance(value, columns.FormattableColumn)
                else value)
            )
        return
