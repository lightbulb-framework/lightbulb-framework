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

"""Application base class for displaying data.
"""
import abc
from itertools import compress

import six
import stevedore

from . import command


@six.add_metaclass(abc.ABCMeta)
class DisplayCommandBase(command.Command):
    """Command base class for displaying data about a single object.
    """

    def __init__(self, app, app_args, cmd_name=None):
        super(DisplayCommandBase, self).__init__(app, app_args,
                                                 cmd_name=cmd_name)
        self._formatter_plugins = self._load_formatter_plugins()

    @abc.abstractproperty
    def formatter_namespace(self):
        "String specifying the namespace to use for loading formatter plugins."

    @abc.abstractproperty
    def formatter_default(self):
        "String specifying the name of the default formatter."

    def _load_formatter_plugins(self):
        # Here so tests can override
        return stevedore.ExtensionManager(
            self.formatter_namespace,
            invoke_on_load=True,
        )

    def get_parser(self, prog_name):
        parser = super(DisplayCommandBase, self).get_parser(prog_name)
        formatter_group = parser.add_argument_group(
            title='output formatters',
            description='output formatter options',
        )
        formatter_choices = sorted(self._formatter_plugins.names())
        formatter_default = self.formatter_default
        if formatter_default not in formatter_choices:
            formatter_default = formatter_choices[0]
        formatter_group.add_argument(
            '-f', '--format',
            dest='formatter',
            action='store',
            choices=formatter_choices,
            default=formatter_default,
            help='the output format, defaults to %s' % formatter_default,
        )
        formatter_group.add_argument(
            '-c', '--column',
            action='append',
            default=[],
            dest='columns',
            metavar='COLUMN',
            help='specify the column(s) to include, can be repeated',
        )
        for formatter in self._formatter_plugins:
            formatter.obj.add_argument_group(parser)
        return parser

    @abc.abstractmethod
    def produce_output(self, parsed_args, column_names, data):
        """Use the formatter to generate the output.

        :param parsed_args: argparse.Namespace instance with argument values
        :param column_names: sequence of strings containing names
                             of output columns
        :param data: iterable with values matching the column names
        """

    def _generate_columns_and_selector(self, parsed_args, column_names):
        """Generate included columns and selector according to parsed args.

        :param parsed_args: argparse.Namespace instance with argument values
        :param column_names: sequence of strings containing names
                             of output columns
        """
        if not parsed_args.columns:
            columns_to_include = column_names
            selector = None
        else:
            columns_to_include = [c for c in column_names
                                  if c in parsed_args.columns]
            if not columns_to_include:
                raise ValueError('No recognized column names in %s' %
                                 str(parsed_args.columns))
            # Set up argument to compress()
            selector = [(c in columns_to_include)
                        for c in column_names]
        return columns_to_include, selector

    def run(self, parsed_args):
        self._run_before_hooks(parsed_args)
        self.formatter = self._formatter_plugins[parsed_args.formatter].obj
        column_names, data = self.take_action(parsed_args)
        self._run_after_hooks(parsed_args, (column_names, data))
        self.produce_output(parsed_args, column_names, data)
        return 0

    @staticmethod
    def _compress_iterable(iterable, selectors):
        return compress(iterable, selectors)
