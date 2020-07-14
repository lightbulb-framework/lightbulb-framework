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

"""Output formatters using PyYAML.
"""

import yaml

from . import base
from cliff import columns


class YAMLFormatter(base.ListFormatter, base.SingleFormatter):

    def add_argument_group(self, parser):
        pass

    def emit_list(self, column_names, data, stdout, parsed_args):
        items = []
        for item in data:
            items.append(
                {n: (i.machine_readable()
                     if isinstance(i, columns.FormattableColumn)
                     else i)
                 for n, i in zip(column_names, item)}
            )
        yaml.safe_dump(items, stream=stdout, default_flow_style=False)

    def emit_one(self, column_names, data, stdout, parsed_args):
        for key, value in zip(column_names, data):
            dict_data = {
                key: (value.machine_readable()
                      if isinstance(value, columns.FormattableColumn)
                      else value)
            }
            yaml.safe_dump(dict_data, stream=stdout, default_flow_style=False)
