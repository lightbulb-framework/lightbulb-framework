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

"""Bash completion for the CLI.
"""

import logging

import six
import stevedore

from cliff import command


class CompleteDictionary:
    """dictionary for bash completion
    """

    def __init__(self):
        self._dictionary = {}

    def add_command(self, command, actions):
        optstr = ' '.join(opt for action in actions
                          for opt in action.option_strings)
        dicto = self._dictionary
        last_cmd = command[-1]
        for subcmd in command[:-1]:
            subdata = dicto.get(subcmd)
            # If there is a string in corresponding dictionary, it means the
            # verb used for the command exists already.
            # For example, {'cmd': 'action'}, and we add the command
            # 'cmd_other'. We want the result to be
            # {'cmd': 'action other', 'cmd_other': 'sub_action'}
            if isinstance(subdata, six.string_types):
                subdata += ' ' + last_cmd
                dicto[subcmd] = subdata
                last_cmd = subcmd + '_' + last_cmd
            else:
                dicto = dicto.setdefault(subcmd, {})
        dicto[last_cmd] = optstr

    def get_commands(self):
        return ' '.join(k for k in sorted(self._dictionary.keys()))

    def _get_data_recurse(self, dictionary, path):
        ray = []
        keys = sorted(dictionary.keys())
        for cmd in keys:
            name = path + "_" + cmd if path else cmd
            value = dictionary[cmd]
            if isinstance(value, six.string_types):
                ray.append((name, value))
            else:
                cmdlist = ' '.join(sorted(value.keys()))
                ray.append((name, cmdlist))
                ray += self._get_data_recurse(value, name)
        return ray

    def get_data(self):
        return sorted(self._get_data_recurse(self._dictionary, ""))


class CompleteShellBase(object):
    """base class for bash completion generation
    """
    def __init__(self, name, output):
        self.name = str(name)
        self.output = output

    def write(self, cmdo, data):
        self.output.write(self.get_header())
        self.output.write("  cmds='{0}'\n".format(cmdo))
        for datum in data:
            datum = (datum[0].replace('-', '_'), datum[1])
            self.output.write('  cmds_{0}=\'{1}\'\n'.format(*datum))
        self.output.write(self.get_trailer())

    @property
    def escaped_name(self):
        return self.name.replace('-', '_')


class CompleteNoCode(CompleteShellBase):
    """completion with no code
    """
    def __init__(self, name, output):
        super(CompleteNoCode, self).__init__(name, output)

    def get_header(self):
        return ''

    def get_trailer(self):
        return ''


class CompleteBash(CompleteShellBase):
    """completion for bash
    """
    def __init__(self, name, output):
        super(CompleteBash, self).__init__(name, output)

    def get_header(self):
        return ('_' + self.escaped_name + """()
{
  local cur prev words
  COMPREPLY=()
  _get_comp_words_by_ref -n : cur prev words

  # Command data:
""")

    def get_trailer(self):
        return ("""
  dash=-
  underscore=_
  cmd=""
  words[0]=""
  completed="${cmds}"
  for var in "${words[@]:1}"
  do
    if [[ ${var} == -* ]] ; then
      break
    fi
    if [ -z "${cmd}" ] ; then
      proposed="${var}"
    else
      proposed="${cmd}_${var}"
    fi
    local i="cmds_${proposed}"
    i=${i//$dash/$underscore}
    local comp="${!i}"
    if [ -z "${comp}" ] ; then
      break
    fi
    if [[ ${comp} == -* ]] ; then
      if [[ ${cur} != -* ]] ; then
        completed=""
        break
      fi
    fi
    cmd="${proposed}"
    completed="${comp}"
  done

  if [ -z "${completed}" ] ; then
    COMPREPLY=( $( compgen -f -- "$cur" ) $( compgen -d -- "$cur" ) )
  else
    COMPREPLY=( $(compgen -W "${completed}" -- ${cur}) )
  fi
  return 0
}
complete -F _""" + self.escaped_name + ' ' + self.name + '\n')


class CompleteCommand(command.Command):
    """print bash completion command
    """

    log = logging.getLogger(__name__ + '.CompleteCommand')

    def __init__(self, app, app_args, cmd_name=None):
        super(CompleteCommand, self).__init__(app, app_args, cmd_name)
        self._formatters = stevedore.ExtensionManager(
            namespace='cliff.formatter.completion',
        )

    def get_parser(self, prog_name):
        parser = super(CompleteCommand, self).get_parser(prog_name)
        parser.add_argument(
            "--name",
            default=None,
            metavar='<command_name>',
            help="Command name to support with command completion"
        )
        parser.add_argument(
            "--shell",
            default='bash',
            metavar='<shell>',
            choices=sorted(self._formatters.names()),
            help="Shell being used. Use none for data only (default: bash)"
        )
        return parser

    def get_actions(self, command):
        the_cmd = self.app.command_manager.find_command(command)
        cmd_factory, cmd_name, search_args = the_cmd
        cmd = cmd_factory(self.app, search_args)
        if self.app.interactive_mode:
            full_name = (cmd_name)
        else:
            full_name = (' '.join([self.app.NAME, cmd_name]))
        cmd_parser = cmd.get_parser(full_name)
        return cmd_parser._get_optional_actions()

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        name = parsed_args.name or self.app.NAME
        try:
            shell_factory = self._formatters[parsed_args.shell].plugin
        except KeyError:
            raise RuntimeError('Unknown shell syntax %r' % parsed_args.shell)
        shell = shell_factory(name, self.app.stdout)

        dicto = CompleteDictionary()
        for cmd in self.app.command_manager:
            command = cmd[0].split()
            dicto.add_command(command, self.get_actions(command))

        shell.write(dicto.get_commands(), dicto.get_data())

        return 0
