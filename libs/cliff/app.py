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

"""Application base class.
"""

import codecs
import inspect
import locale
import logging
import logging.handlers
import os
import six
import sys

from cliff import _argparse
from . import complete
from . import help
from . import utils


logging.getLogger('cliff').addHandler(logging.NullHandler())


class App(object):
    """Application base class.

    :param description: one-liner explaining the program purpose
    :paramtype description: str
    :param version: application version number
    :paramtype version: str
    :param command_manager: plugin loader
    :paramtype command_manager: cliff.commandmanager.CommandManager
    :param stdin: Standard input stream
    :paramtype stdin: readable I/O stream
    :param stdout: Standard output stream
    :paramtype stdout: writable I/O stream
    :param stderr: Standard error output stream
    :paramtype stderr: writable I/O stream
    :param interactive_app_factory: callable to create an
                                    interactive application
    :paramtype interactive_app_factory: cliff.interactive.InteractiveApp
    :param deferred_help: True - Allow subcommands to accept --help with
                          allowing to defer help print after initialize_app
    :paramtype deferred_help: bool
    """

    NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    LOG = logging.getLogger(NAME)

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'
    DEFAULT_VERBOSE_LEVEL = 1
    DEFAULT_OUTPUT_ENCODING = 'utf-8'

    def __init__(self, description, version, command_manager,
                 stdin=None, stdout=None, stderr=None,
                 interactive_app_factory=None,
                 deferred_help=False):
        """Initialize the application.
        """
        self.command_manager = command_manager
        self.command_manager.add_command('help', help.HelpCommand)
        self.command_manager.add_command('complete', complete.CompleteCommand)
        self._set_streams(stdin, stdout, stderr)
        self.interactive_app_factory = interactive_app_factory
        self.deferred_help = deferred_help
        self.parser = self.build_option_parser(description, version)
        self.interactive_mode = False
        self.interpreter = None

    def _set_streams(self, stdin, stdout, stderr):
        try:
            locale.setlocale(locale.LC_ALL, '')
        except locale.Error:
            pass

        # Unicode must be encoded/decoded for text I/O streams, the
        # correct encoding for the stream must be selected and it must
        # be capable of handling the set of characters in the stream
        # or Python will raise a codec error. The correct codec is
        # selected based on the locale. Python2 uses the locales
        # encoding but only when the I/O stream is attached to a
        # terminal (TTY) otherwise it uses the default ASCII
        # encoding. The effect is internationalized text written to
        # the terminal works as expected but if command line output is
        # redirected (file or pipe) the ASCII codec is used and the
        # program aborts with a codec error.
        #
        # The default I/O streams stdin, stdout and stderr can be
        # wrapped in a codec based on the locale thus assuring the
        # users desired encoding is always used no matter the I/O
        # destination. Python3 does this by default.
        #
        # If the caller supplies an I/O stream we use it unmodified on
        # the assumption the caller has taken all responsibility for
        # the stream.  But with Python2 if the caller allows us to
        # default the I/O streams to sys.stdin, sys.stdout and
        # sys.stderr we apply the locales encoding just as Python3
        # would do. We also check to make sure the main Python program
        # has not already already wrapped sys.stdin, sys.stdout and
        # sys.stderr as this is a common recommendation.

        if six.PY2:
            encoding = locale.getpreferredencoding()
            if encoding:
                if not (stdin or isinstance(sys.stdin, codecs.StreamReader)):
                    stdin = codecs.getreader(encoding)(sys.stdin)

                if not (stdout or isinstance(sys.stdout, codecs.StreamWriter)):
                    stdout = codecs.getwriter(encoding)(sys.stdout)

                if not (stderr or isinstance(sys.stderr, codecs.StreamWriter)):
                    stderr = codecs.getwriter(encoding)(sys.stderr)

        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}
        parser = _argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
        )
        verbose_group = parser.add_mutually_exclusive_group()
        verbose_group.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        verbose_group.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        if self.deferred_help:
            parser.add_argument(
                '-h', '--help',
                dest='deferred_help',
                action='store_true',
                help="Show help message and exit.",
            )
        else:
            parser.add_argument(
                '-h', '--help',
                action=help.HelpAction,
                nargs=0,
                default=self,  # tricky
                help="Show help message and exit.",
            )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )
        return parser

    def configure_logging(self):
        """Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        # Set up logging to a file
        if self.options.log_file:
            file_handler = logging.FileHandler(
                filename=self.options.log_file,
            )
            formatter = logging.Formatter(self.LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Always send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
        console_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)
        formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)
        return

    def print_help_if_requested(self):
        """Print help and exits if deferred help is enabled and requested.

        '--help' shows the help message and exits:
         * without calling initialize_app if not self.deferred_help (default),
         * after initialize_app call if self.deferred_help,
         * during initialize_app call if self.deferred_help and subclass calls
           explicitly this method in initialize_app.
        """
        if self.deferred_help and self.options.deferred_help:
            action = help.HelpAction(None, None, default=self)
            action(self.parser, self.options, None, None)

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            self.options, remainder = self.parser.parse_known_args(argv)
            self.configure_logging()
            self.interactive_mode = not remainder
            if self.deferred_help and self.options.deferred_help and remainder:
                # When help is requested and `remainder` has any values disable
                # `deferred_help` and instead allow the help subcommand to
                # handle the request during run_subcommand(). This turns
                # "app foo bar --help" into "app help foo bar". However, when
                # `remainder` is empty use print_help_if_requested() to allow
                # for an early exit.
                # Disabling `deferred_help` here also ensures that
                # print_help_if_requested will not fire if called by a subclass
                # during its initialize_app().
                self.options.deferred_help = False
                remainder.insert(0, "help")
            self.initialize_app(remainder)
            self.print_help_if_requested()
        except Exception as err:
            if hasattr(self, 'options'):
                debug = self.options.debug
            else:
                debug = True
            if debug:
                self.LOG.exception(err)
                raise
            else:
                self.LOG.error(err)
            return 1
        result = 1
        if self.interactive_mode:
            result = self.interact()
        else:
            result = self.run_subcommand(remainder)
        return result

    # FIXME(dhellmann): Consider moving these command handling methods
    # to a separate class.
    def initialize_app(self, argv):
        """Hook for subclasses to take global initialization action
        after the arguments are parsed but before a command is run.
        Invoked only once, even in interactive mode.

        :param argv: List of arguments, including the subcommand to run.
                     Empty for interactive mode.
        """
        return

    def prepare_to_run_command(self, cmd):
        """Perform any preliminary work needed to run a command.

        :param cmd: command processor being invoked
        :paramtype cmd: cliff.command.Command
        """
        return

    def clean_up(self, cmd, result, err):
        """Hook run after a command is done to shutdown the app.

        :param cmd: command processor being invoked
        :paramtype cmd: cliff.command.Command
        :param result: return value of cmd
        :paramtype result: int
        :param err: exception or None
        :paramtype err: Exception
        """
        return

    def interact(self):
        # Defer importing .interactive as cmd2 is a slow import
        from .interactive import InteractiveApp

        if self.interactive_app_factory is None:
            self.interactive_app_factory = InteractiveApp
        self.interpreter = self.interactive_app_factory(self,
                                                        self.command_manager,
                                                        self.stdin,
                                                        self.stdout,
                                                        )
        self.interpreter.cmdloop()
        return 0

    def get_fuzzy_matches(self, cmd):
        """return fuzzy matches of unknown command
        """

        sep = '_'
        if self.command_manager.convert_underscores:
            sep = ' '
        all_cmds = [k[0] for k in self.command_manager]
        dist = []
        for candidate in sorted(all_cmds):
            prefix = candidate.split(sep)[0]
            # Give prefix match a very good score
            if candidate.startswith(cmd):
                dist.append((0, candidate))
                continue
            # Levenshtein distance
            dist.append((utils.damerau_levenshtein(cmd, prefix, utils.COST)+1,
                         candidate))

        matches = []
        match_distance = 0
        for distance, candidate in sorted(dist):
            if distance > match_distance:
                if match_distance:
                    # we copied all items with minimum distance, we are done
                    break
                # we copied all items with distance=0,
                # now we match all candidates at the minimum distance
                match_distance = distance
            matches.append(candidate)

        return matches

    def run_subcommand(self, argv):
        try:
            subcommand = self.command_manager.find_command(argv)
        except ValueError as err:
            # If there was no exact match, try to find a fuzzy match
            the_cmd = argv[0]
            fuzzy_matches = self.get_fuzzy_matches(the_cmd)
            if fuzzy_matches:
                article = 'a'
                if self.NAME[0] in 'aeiou':
                    article = 'an'
                self.stdout.write('%s: \'%s\' is not %s %s command. '
                                  'See \'%s --help\'.\n'
                                  % (self.NAME, ' '.join(argv), article,
                                      self.NAME, self.NAME))
                self.stdout.write('Did you mean one of these?\n')
                for match in fuzzy_matches:
                    self.stdout.write('  %s\n' % match)
            else:
                if self.options.debug:
                    raise
                else:
                    self.LOG.error(err)
            return 2
        cmd_factory, cmd_name, sub_argv = subcommand
        kwargs = {}
        if 'cmd_name' in inspect.getargspec(cmd_factory.__init__).args:
            kwargs['cmd_name'] = cmd_name
        cmd = cmd_factory(self, self.options, **kwargs)
        err = None
        result = 1
        try:
            self.prepare_to_run_command(cmd)
            full_name = (cmd_name
                         if self.interactive_mode
                         else ' '.join([self.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
            parsed_args = cmd_parser.parse_args(sub_argv)
            result = cmd.run(parsed_args)
        except Exception as err:
            if self.options.debug:
                self.LOG.exception(err)
            else:
                self.LOG.error(err)
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    self.LOG.exception(err2)
                else:
                    self.LOG.error('Could not clean up: %s', err2)
            if self.options.debug:
                raise
        else:
            try:
                self.clean_up(cmd, result, None)
            except Exception as err3:
                if self.options.debug:
                    self.LOG.exception(err3)
                else:
                    self.LOG.error('Could not clean up: %s', err3)
        return result
