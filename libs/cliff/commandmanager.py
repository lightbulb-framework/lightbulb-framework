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

"""Discover and lookup command plugins.
"""

import inspect
import logging

import pkg_resources


LOG = logging.getLogger(__name__)


class EntryPointWrapper(object):
    """Wrap up a command class already imported to make it look like a plugin.
    """

    def __init__(self, name, command_class):
        self.name = name
        self.command_class = command_class

    def load(self, require=False):
        return self.command_class


class CommandManager(object):
    """Discovers commands and handles lookup based on argv data.

    :param namespace: String containing the setuptools entrypoint namespace
                      for the plugins to be loaded. For example,
                      ``'cliff.formatter.list'``.
    :param convert_underscores: Whether cliff should convert underscores to
                                spaces in entry_point commands.
    """
    def __init__(self, namespace, convert_underscores=True):
        self.commands = {}
        self.namespace = namespace
        self.convert_underscores = convert_underscores
        self._load_commands()

    def _load_commands(self):
        # NOTE(jamielennox): kept for compatibility.
        self.load_commands(self.namespace)

    def load_commands(self, namespace):
        """Load all the commands from an entrypoint"""
        for ep in pkg_resources.iter_entry_points(namespace):
            LOG.debug('found command %r', ep.name)
            cmd_name = (ep.name.replace('_', ' ')
                        if self.convert_underscores
                        else ep.name)
            self.commands[cmd_name] = ep
        return

    def __iter__(self):
        return iter(self.commands.items())

    def add_command(self, name, command_class):
        self.commands[name] = EntryPointWrapper(name, command_class)

    def find_command(self, argv):
        """Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        start = self._get_last_possible_command_index(argv)
        for i in range(start, 0, -1):
            name = ' '.join(argv[:i])
            search_args = argv[i:]
            if name in self.commands:
                cmd_ep = self.commands[name]
                if hasattr(cmd_ep, 'resolve'):
                    cmd_factory = cmd_ep.resolve()
                else:
                    # NOTE(dhellmann): Some fake classes don't take
                    # require as an argument. Yay?
                    arg_spec = inspect.getargspec(cmd_ep.load)
                    if 'require' in arg_spec[0]:
                        cmd_factory = cmd_ep.load(require=False)
                    else:
                        cmd_factory = cmd_ep.load()
                return (cmd_factory, name, search_args)
        else:
            raise ValueError('Unknown command %r' %
                             (argv,))

    def _get_last_possible_command_index(self, argv):
        """Returns the index after the last argument
        in argv that can be a command word
        """
        for i, arg in enumerate(argv):
            if arg.startswith('-'):
                return i
        return len(argv)
