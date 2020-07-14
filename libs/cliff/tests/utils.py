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

from cliff.command import Command
from cliff.commandmanager import CommandManager

TEST_NAMESPACE = 'cliff.test'


class TestParser(object):

    def print_help(self, stdout):
        stdout.write('TestParser')


class TestCommand(Command):
    "Test command."

    def get_parser(self, ignore):
        # Make it look like this class is the parser
        # so parse_args() is called.
        return TestParser()

    def take_action(self, args):
        return


class TestDeprecatedCommand(TestCommand):

    deprecated = True


class TestCommandManager(CommandManager):

    def load_commands(self, namespace):
        if namespace == TEST_NAMESPACE:
            for key in ('one', 'two words', 'three word command'):
                self.add_command(key, TestCommand)
            self.add_command('old cmd', TestDeprecatedCommand)
