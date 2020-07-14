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

"""Formattable column tools.
"""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class FormattableColumn(object):

    def __init__(self, value):
        self._value = value

    @abc.abstractmethod
    def human_readable(self):
        """Return a basic human readable version of the data.
        """

    def machine_readable(self):
        """Return a raw data structure using only Python built-in types.

        It must be possible to serialize the return value directly
        using a formatter like JSON, and it will be up to the
        formatter plugin to decide how to make that transformation.

        """
        return self._value
