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

"""Base classes for formatters.
"""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Formatter(object):

    @abc.abstractmethod
    def add_argument_group(self, parser):
        """Add any options to the argument parser.

        Should use our own argument group.
        """


@six.add_metaclass(abc.ABCMeta)
class ListFormatter(Formatter):
    """Base class for formatters that know how to deal with multiple objects.
    """

    @abc.abstractmethod
    def emit_list(self, column_names, data, stdout, parsed_args):
        """Format and print the list from the iterable data source.

        Data values can be primitive types like ints and strings, or
        can be an instance of a :class:`FormattableColumn` for
        situations where the value is complex, and may need to be
        handled differently for human readable output vs. machine
        readable output.

        :param column_names: names of the columns
        :param data: iterable data source, one tuple per object
                     with values in order of column names
        :param stdout: output stream where data should be written
        :param parsed_args: argparse namespace from our local options

        """


@six.add_metaclass(abc.ABCMeta)
class SingleFormatter(Formatter):
    """Base class for formatters that work with single objects.
    """

    @abc.abstractmethod
    def emit_one(self, column_names, data, stdout, parsed_args):
        """Format and print the values associated with the single object.

        Data values can be primitive types like ints and strings, or
        can be an instance of a :class:`FormattableColumn` for
        situations where the value is complex, and may need to be
        handled differently for human readable output vs. machine
        readable output.

        :param column_names: names of the columns
        :param data: iterable data source with values in order of column names
        :param stdout: output stream where data should be written
        :param parsed_args: argparse namespace from our local options
        """
