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

import functools

from cliff import command
from cliff.tests import base


class TestCommand(command.Command):
    """Description of command.
    """

    def get_parser(self, prog_name):
        parser = super(TestCommand, self).get_parser(prog_name)
        parser.add_argument(
            'long_help_argument',
            help="Create a NIC on the server.\n"
                 "Specify option multiple times to create multiple NICs. "
                 "Either net-id or port-id must be provided, but not both.\n"
                 "net-id: attach NIC to network with this UUID\n"
                 "port-id: attach NIC to port with this UUID\n"
                 "v4-fixed-ip: IPv4 fixed address for NIC (optional)\n"
                 "v6-fixed-ip: IPv6 fixed address for NIC (optional)\n"
                 "none: (v2.37+) no network is attached\n"
                 "auto: (v2.37+) the compute service will automatically "
                 "allocate a network.\n"
                 "Specifying a --nic of auto or none "
                 "cannot be used with any other --nic value.",
        )
        parser.add_argument(
            'regular_help_argument',
            help="The quick brown fox jumps "
                 "over the lazy dog.",
        )
        return parser

    def take_action(self, parsed_args):
        return 42


class TestCommandNoDocstring(command.Command):

    def take_action(self, parsed_args):
        return 42


class TestDescription(base.TestBase):

    def test_get_description_docstring(self):
        cmd = TestCommand(None, None)
        desc = cmd.get_description()
        assert desc == "Description of command.\n    "

    def test_get_description_attribute(self):
        cmd = TestCommand(None, None)
        # Artificially inject a value for _description to verify that it
        # overrides the docstring.
        cmd._description = 'this is not the default'
        desc = cmd.get_description()
        assert desc == 'this is not the default'

    def test_get_description_default(self):
        cmd = TestCommandNoDocstring(None, None)
        desc = cmd.get_description()
        assert desc == ''


class TestBasicValues(base.TestBase):

    def test_get_parser(self):
        cmd = TestCommand(None, None)
        parser = cmd.get_parser('NAME')
        assert parser.prog == 'NAME'

    def test_get_name(self):
        cmd = TestCommand(None, None, cmd_name='object action')
        assert cmd.cmd_name == 'object action'

    def test_run_return(self):
        cmd = TestCommand(None, None, cmd_name='object action')
        assert cmd.run(None) == 42


expected_help_message = """
  long_help_argument    Create a NIC on the server.
                        Specify option multiple times to create multiple NICs.
                        Either net-id or port-id must be provided, but not
                        both.
                        net-id: attach NIC to network with this UUID
                        port-id: attach NIC to port with this UUID
                        v4-fixed-ip: IPv4 fixed address for NIC (optional)
                        v6-fixed-ip: IPv6 fixed address for NIC (optional)
                        none: (v2.37+) no network is attached
                        auto: (v2.37+) the compute service will automatically
                        allocate a network.
                        Specifying a --nic of auto or none cannot be used with
                        any other --nic value.
  regular_help_argument
                        The quick brown fox jumps over the lazy dog.
"""


class TestHelp(base.TestBase):

    def test_smart_help_formatter(self):
        cmd = TestCommand(None, None)
        parser = cmd.get_parser('NAME')
        # Set up the formatter to always use a width=80 so that the
        # terminal width of the developer's system does not cause the
        # test to fail. Trying to mock os.environ failed, but there is
        # an arg to HelpFormatter to set the width
        # explicitly. Unfortunately, there is no way to do that
        # through the parser, so we have to replace the parser's
        # formatter_class attribute with a partial() that passes width
        # to the original class.
        parser.formatter_class = functools.partial(
            parser.formatter_class,
            width=78,
        )
        self.assertIn(expected_help_message, parser.format_help())
