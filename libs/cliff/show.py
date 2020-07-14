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

"""Application base class for displaying data about a single object.
"""
import abc

import six

from . import display


@six.add_metaclass(abc.ABCMeta)
class ShowOne(display.DisplayCommandBase):
    """Command base class for displaying data about a single object.
    """

    @property
    def formatter_namespace(self):
        return 'cliff.formatter.show'

    @property
    def formatter_default(self):
        return 'table'

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Return a two-part tuple with a tuple of column names
        and a tuple of values.
        """

    def produce_output(self, parsed_args, column_names, data):
        (columns_to_include, selector) = self._generate_columns_and_selector(
            parsed_args, column_names)
        if selector:
            data = list(self._compress_iterable(data, selector))
        self.formatter.emit_one(columns_to_include,
                                data,
                                self.app.stdout,
                                parsed_args)
        return 0

    def dict2columns(self, data):
        """Implement the common task of converting a dict-based object
        to the two-column output that ShowOne expects.
        """
        if not data:
            return ({}, {})
        else:
            return zip(*sorted(data.items()))
