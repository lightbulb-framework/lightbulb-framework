"""
This module transforms a file containing regular expressions for flex parser
into a DFA object (pyfst automaton)
"""
import os
import random
import re
import string
import tempfile
from subprocess import call
from sys import argv

from alphabet import createalphabet
from dfa import DFA


class Flexparser:
    """
    This class parses compiles a file containing regular
    expressions into a flex compiled file, and then parses
    the flex DFA into a pyfst DFA
    """

    outfile = ""

    def __init__(self, alphabet=None):
        """
        Initialization function
        Args:
            alphabet (list): input alphabet
        Returns:
            None
        """
        if alphabet is not None:
            self.alphabet = alphabet
        else:
            self.alphabet = []

    def _create_automaton_from_regex(self, myfile):
        """
        Generates a flex compiled file using myfile
        as input
        Args:
            myfile (str): Flex file to be parsed
        Returns:
            None
        """
        call(["flex", "-o", self.outfile, "-f", myfile])

    def _read_transitions(self):
        """
        Read DFA transitions from flex compiled file
        Args:
            None
        Returns:
            list: The list of states and the destination for a character
        """
        states = []
        i = 0
        regex = re.compile('[ \t\n\r:,]+')
        found = 0  # For maintaining the state of yy_nxt declaration
        state = 0  # For maintaining the state of opening and closing tag of yy_nxt
        substate = 0  # For maintaining the state of opening and closing tag of each set in yy_nxt
        mapping = []  # For writing each set of yy_next
        cur_line = None
        with open(self.outfile) as flex_file:
            for cur_line in flex_file:
                if cur_line[0:35] == "static yyconst flex_int16_t yy_nxt[" or cur_line[0:33] == "static const flex_int16_t yy_nxt[":
                    found = 1
                    # print 'Found yy_next declaration'
                    continue
                if found == 1:
                    if state == 0 and cur_line[0:5] == "    {":
                        state = 1
                        continue
                    if state == 1 and cur_line[0:7] == "    } ;":
                        state = 0
                        break

                    if substate == 0 and cur_line[0:5] == "    {":
                        mapping = []
                        substate = 1
                        continue
                    if substate == 1:
                        if cur_line[0:6] != "    },":
                            cur_line = "".join(cur_line.split())
                            if cur_line == '':
                                continue
                            if cur_line[cur_line.__len__() - 1] == ',':
                                splitted_line = regex.split(
                                    cur_line[:cur_line.__len__() - 1])
                            else:
                                splitted_line = regex.split(cur_line)
                            mapping = mapping + splitted_line
                            continue
                        else:
                            cleared = []
                            for j in mapping:
                                cleared.append(int(j))
                            states.append(cleared)
                            mapping = []
                            substate = 0

        return states

    def _read_accept_states(self):
        """
        Read DFA accepted states from flex compiled file
        Args:
            None
        Returns:
            list: The list of accepted states
        """
        states = []
        i = 0
        regex = re.compile('[ \t\n\r:,]+')
        found = 0  # For maintaining the state of yy_accept declaration
        state = 0  # For maintaining the state of opening and closing tag of yy_accept
        mapping = [] # For writing each set of yy_accept
        cur_line = None
        with open(self.outfile) as flex_file:
            for cur_line in flex_file:
                if cur_line[0:37] == "static yyconst flex_int16_t yy_accept" or cur_line[0:35] == "static const flex_int16_t yy_accept":
                    found = 1
                    continue
                if found == 1:
                    # print x
                    if state == 0 and cur_line[0:5] == "    {":
                        mapping.append(0)  # there is always a zero there
                        state = 1
                        continue

                    if state == 1:
                        if cur_line[0:7] != "    } ;":
                            cur_line = "".join(cur_line.split())
                            if cur_line == '':
                                continue
                            if cur_line[cur_line.__len__() - 1] == ',':
                                splitted_line = regex.split(
                                    cur_line[:cur_line.__len__() - 1])
                            else:
                                splitted_line = regex.split(cur_line)
                            mapping = mapping + splitted_line
                            continue
                        else:
                            cleared = []
                            for j in mapping:
                                cleared.append(int(j))
                            max_value = max(cleared)
                            for i in range(0, len(cleared)):
                                if cleared[i] > 0 and cleared[
                                        i] < (max_value - 1):
                                    states.append(i)
                            return states
        return []

    def _read_null_transitions(self):
        """
        Read DFA'input_string NULL transitions from flex compiled file
        Args:
            None
        Returns:
            list: The list of state transitions for no character
        """
        states = []
        regex = re.compile('[ \t\n\r:,]+')
        found = 0  # For maintaining the state of yy_NUL_trans declaration
        state = 0  # For maintaining the state of opening and closing tag of yy_NUL_trans
        mapping = []  # For writing each set of yy_NUL_trans
        cur_line = None
        with open(self.outfile) as flex_file:
            for cur_line in flex_file:
                if cur_line[0:len("static yyconst yy_state_type yy_NUL_trans")
                            ] == "static yyconst yy_state_type yy_NUL_trans" or cur_line[0:len("static const yy_state_type yy_NUL_trans")
                            ] == "static const yy_state_type yy_NUL_trans":
                    found = 1
                    # print 'Found yy_next declaration'
                    continue
                if found == 1:
                    if state == 0 and cur_line[0:5] == "    {":
                        mapping.append(0)  # there is always a zero there
                        state = 1
                        continue
                    if state == 1:
                        if cur_line[0:7] != "    } ;":
                            cur_line = "".join(cur_line.split())
                            if cur_line == '':
                                continue
                            if cur_line[cur_line.__len__() - 1] == ',':
                                splitted_line = regex.split(
                                    cur_line[:cur_line.__len__() - 1])
                            else:
                                splitted_line = regex.split(cur_line)
                                #  print y
                            mapping = mapping + splitted_line
                            continue
                        else:
                            cleared = []
                            for j in mapping:
                                cleared.append(int(j))
                            states = cleared
                            mapping = []
                            state = 0

        return states

    def _create_states(self, states_num):
        """
        Args:
            states_num (int): Number of States
        Returns:
            list: An initialized list
        """
        states = []
        for i in range(0, states_num):
            states.append(i)
        return states

    def _add_sink_state(self, states):
        """
        This function adds a sing state in the total states
        Args:
            states (list): The current states
        Returns:
            None
        """
        cleared = []
        for i in range(0, 128):
            cleared.append(-1)
        states.append(cleared)

    def _create_delta(self):
        """
        This function creates the delta transition
        Args:
            startState (int): Initial state of automaton
        Results:
            int, func: A number indicating the total states, and the delta function
        """
        states = self._read_transitions()
        total_states = len(states)
        self._add_sink_state(states)
        nulltrans = self._read_null_transitions()

        def delta(current_state, character):
            """
            Sub function describing the transitions
            Args:
                current_state (str): The current state
                character (str): The input character
            Returns:
                str: The next state
            """
            if character != '':
                newstate = states[current_state][ord(character)]
                if newstate > 0:
                    return newstate
                else:
                    return total_states
            else:
                return nulltrans[current_state]

        return total_states + 1, delta

    def yyparse(self, lexfile):
        """
        Args:
            lexfile (str): Flex file to be parsed
        Returns:
            DFA: A dfa automaton
        """
        temp = tempfile.gettempdir()
        self.outfile = temp+'/'+''.join(
            random.choice(
                string.ascii_uppercase + string.digits) for _ in range(5)) + '_lex.yy.c'
        self._create_automaton_from_regex(lexfile)
        states_num, delta = self._create_delta()
        states = self._create_states(states_num)
        accepted_states = self._read_accept_states()
        if self.alphabet != []:
            alphabet = self.alphabet
        else:
            alphabet = createalphabet()
        mma = DFA(alphabet)
        for state in states:
            if state != 0:
                for char in alphabet:
                    nextstate = delta(state, char)
                    mma.add_arc(state - 1, nextstate - 1, char)
                if state in accepted_states:
                    mma[state - 1].final = True
        if os.path.exists(self.outfile):
            os.remove(self.outfile)
        return mma


def main():
    """
    Testing function for Flex Regular Expressions to FST DFA
    """
    if len(argv) < 2:
        print 'Usage: %s fst_file [optional: save_file]' % argv[0]
        return
    flex_a = Flexparser()
    mma = flex_a.yyparse(argv[1])
    mma.minimize()
    print mma
    if len(argv) == 3:
        mma.save(argv[2])


if __name__ == '__main__':
    main()