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
import inspect

import six
from stevedore import extension

from cliff import _argparse


@six.add_metaclass(abc.ABCMeta)
class Command(object):
    """Base class for command plugins.

    When the command is instantiated, it loads extensions from a
    namespace based on the parent application namespace and the
    command name::

        app.namespace + '.' + cmd_name.replace(' ', '_')

    :param app: Application instance invoking the command.
    :paramtype app: cliff.app.App

    """

    deprecated = False

    _description = ''
    _epilog = None

    def __init__(self, app, app_args, cmd_name=None):
        self.app = app
        self.app_args = app_args
        self.cmd_name = cmd_name
        self._load_hooks()

    def _load_hooks(self):
        # Look for command extensions
        if self.app and self.cmd_name:
            namespace = '{}.{}'.format(
                self.app.command_manager.namespace,
                self.cmd_name.replace(' ', '_')
            )
            self._hooks = extension.ExtensionManager(
                namespace=namespace,
                invoke_on_load=True,
                invoke_kwds={
                    'command': self,
                },
            )
        else:
            # Setting _hooks to an empty list allows iteration without
            # checking if there are hooks every time.
            self._hooks = []
        return

    def get_description(self):
        """Return the command description.

        The default is to use the first line of the class' docstring
        as the description. Set the ``_description`` class attribute
        to a one-line description of a command to use a different
        value. This is useful for enabling translations, for example,
        with ``_description`` set to a string wrapped with a gettext
        translation marker.

        """
        # NOTE(dhellmann): We need the trailing "or ''" because under
        # Python 2.7 the default for the docstring is None instead of
        # an empty string, and we always want this method to return a
        # string.
        desc = self._description or inspect.getdoc(self.__class__) or ''
        # The base class command description isn't useful for any
        # real commands, so ignore that value.
        if desc == inspect.getdoc(Command):
            desc = ''
        return desc

    def get_epilog(self):
        """Return the command epilog."""
        hook_epilogs = filter(
            None,
            (h.obj.get_epilog() for h in self._hooks),
        )
        if hook_epilogs:
            # combine them, replacing a None in self._epilog with an
            # empty string
            parts = [self._epilog or '']
            parts.extend(hook_epilogs)
            return '\n\n'.join(parts)
        return self._epilog

    def get_parser(self, prog_name):
        """Return an :class:`argparse.ArgumentParser`.
        """
        parser = _argparse.ArgumentParser(
            description=self.get_description(),
            epilog=self.get_epilog(),
            prog=prog_name,
            formatter_class=_SmartHelpFormatter,
        )
        for hook in self._hooks:
            hook.obj.get_parser(parser)
        return parser

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Override to do something useful.

        The returned value will be returned by the program.
        """

    def run(self, parsed_args):
        """Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        Developers creating new command base classes (such as
        :class:`Lister` and :class:`ShowOne`) should override this
        method to wrap :meth:`take_action`.

        Return the value returned by :meth:`take_action` or 0.
        """
        self._run_before_hooks(parsed_args)
        return_code = self.take_action(parsed_args) or 0
        self._run_after_hooks(parsed_args, return_code)
        return return_code

    def _run_before_hooks(self, parsed_args):
        """Calls before() method of the hooks.

        This method is intended to be called from the run() method before
        take_action() is called.

        This method should only be overriden by developers creating new
        command base classes and only if it is necessary to have different
        hook processing behavior.
        """
        for hook in self._hooks:
            hook.obj.before(parsed_args)

    def _run_after_hooks(self, parsed_args, return_code):
        """Calls after() method of the hooks.

        This method is intended to be called from the run() method after
        take_action() is called.

        This method should only be overriden by developers creating new
        command base classes and only if it is necessary to have different
        hook processing behavior.
        """
        for hook in self._hooks:
            hook.obj.after(parsed_args, return_code)


class _SmartHelpFormatter(_argparse.HelpFormatter):
    """Smart help formatter to output raw help message if help contain \n.

    Some command help messages maybe have multiple line content, the built-in
    argparse.HelpFormatter wrap and split the content according to width, and
    ignore \n in the raw help message, it merge multiple line content in one
    line to output, that looks messy. SmartHelpFormatter keep the raw help
    message format if it contain \n, and wrap long line like HelpFormatter
    behavior.
    """

    def _split_lines(self, text, width):
        lines = text.splitlines() if '\n' in text else [text]
        wrap_lines = []
        for each_line in lines:
            wrap_lines.extend(
                super(_SmartHelpFormatter, self)._split_lines(each_line, width)
            )
        return wrap_lines
