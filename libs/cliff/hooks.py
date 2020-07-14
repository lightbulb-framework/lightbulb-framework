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

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class CommandHook(object):
    """Base class for command hooks.

    :param app: Command instance being invoked
    :paramtype app: cliff.command.Command

    """

    def __init__(self, command):
        self.cmd = command

    @abc.abstractmethod
    def get_parser(self, parser):
        """Return an :class:`argparse.ArgumentParser`.

        :param parser: An existing ArgumentParser instance to be modified.
        :paramtype parser: ArgumentParser
        :returns: ArgumentParser
        """
        return parser

    @abc.abstractmethod
    def get_epilog(self):
        "Return text to add to the command help epilog."
        return ''

    @abc.abstractmethod
    def before(self, parsed_args):
        """Called before the command's take_action() method.

        Any return value is ignored.

        :param parsed_args: The arguments to the command.
        :paramtype parsed_args: argparse.Namespace
        """

    @abc.abstractmethod
    def after(self, parsed_args, return_code):
        """Called after the command's take_action() method.

        Any return value is ignored.

        :param parsed_args: The arguments to the command.
        :paramtype parsed_args: argparse.Namespace
        :param return_code: The value returned from take_action().
        :paramtype return_code: int
        """
