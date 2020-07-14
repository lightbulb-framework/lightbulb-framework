"""
This module performs all basic DFA operations.
It is an interface for pyfst.
"""
# /usr/bin/python

from operator import attrgetter
import fst
from alphabet import createalphabet

EPSILON = fst.EPSILON

def TropicalWeight(param):
    """
    Returns fst TropicalWeight
    Args:
        param (str): The input
    Returns:
        bool: The arc weight
    """
    return fst.TropicalWeight(param)

class FstDFA(fst.StdAcceptor):
    """
    Contains extra method to consume input and produce outputs.
    The underline library is pyfst, the python bindings of openFST library.
    """

    def __init__(self, alphabet = createalphabet()):
        """
        Args:
            alphabet (list): pyfst input symbol list
        Returns:
            None
        """
        isyms = None
        self.alphabet = alphabet
        fst.StdAcceptor.__init__(self, isyms)
        num = 1
        for char in self.alphabet:
            self.isyms.__setitem__(char, num)
            num = num + 1

    def fixminimized(self, alphabet):
        """
        After pyfst minimization,
        all unused arcs are removed,
        and all sink states are removed.
        However this may break compatibility.
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        endstate = len(list(self.states))
        for state in self.states:
            for char in alphabet:
                found = 0
                for arc in state.arcs:
                    if self.isyms.find(arc.ilabel) == char:
                        found = 1
                        break
                if found == 0:
                    self.add_arc(state.stateid, endstate, char)

        self[endstate].final = TropicalWeight(float('inf'))

        for char in alphabet:
            self.add_arc(endstate, endstate, char)

    def _addsink(self, alphabet):
        """
        Adds a sink state
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        endstate = len(list(self.states))
        for state in self.states:
            for char in alphabet:
                found = 0
                for arc in state.arcs:
                    if self.isyms.find(arc.ilabel) == char:
                        found = 1
                        break
                if found == 0:
                    self.add_arc(state.stateid, endstate, char)

        self[endstate].final = TropicalWeight(float('inf'))

        for char in alphabet:
            self.add_arc(endstate, endstate, char)

    def _path_to_str(self, path):
        """
        Convert a path to the string representing the path
        Args:
            path (tuple): A tuple of arcs
        Returns:
            inp (str): The path concatenated as as string
        """
        inp = ''
        for arc in path:
            i = self.isyms.find(arc.ilabel)
            # Ignore \epsilon transitions both on input
            if i != fst.EPSILON:
                inp += i
        return inp

    def init_from_acceptor(self, acceptor):
        """
        Adds a sink state
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        states = sorted(
            acceptor.states,
            key=attrgetter('initial'),
            reverse=True)
        for state in states:
            for arc in state.arcs:
                itext = acceptor.isyms.find(arc.ilabel)
                if itext in self.alphabet:
                    self.add_arc(state.stateid, arc.nextstate, itext)
            if state.final:
                self[state.stateid].final = True
            if state.initial:
                self[state.stateid].initial = True

    def consume_input(self, inp):
        """
        Return True/False if the machine accepts/reject the input.
        Args:
            inp (str): input string to be consumed
        Returns:
            bool: A true or false value depending on if the DFA
                accepts the provided input
        """
        cur_state = sorted(
            self.states,
            key=attrgetter('initial'),
            reverse=True)[0]
        while len(inp) > 0:
            found = False
            for arc in cur_state.arcs:
                if self.isyms.find(arc.ilabel) == inp[0]:
                    cur_state = self[arc.nextstate]
                    inp = inp[1:]
                    found = True
                    break
            if not found:
                return False
        return cur_state.final != TropicalWeight(float('inf'))

    def empty(self):
        """""
        Return True if the DFA accepts the empty language.
        """
        return len(list(self.states)) == 0

    def random_strings(self, string_length=1):
        """
        Generate string_length random strings that belong to the automaton.
        Args:
            string_length (integer): The size of the random string
        Returns:
            str: The generated string
        """
        str_list = []
        for path in self.uniform_generate(string_length):
            str_list.append(self._path_to_str(path))
        return str_list

    def complement(self, alphabet):
        """
        Generate the complement of a DFA automaton
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        self._addsink(alphabet)
        states = sorted(self.states, key=attrgetter('initial'), reverse=True)
        for state in states:
            if state.final:
                state.final = False
            else:
                state.final = True

    def save(self, txt_fst_filename):
        """
        Save the machine in the openFST format in the file denoted by
        txt_fst_filename.
        Args:
            txt_fst_filename (str): The name of the file
        Returns:
            None
        """
        txt_fst = open(txt_fst_filename, 'w+')
        states = sorted(self.states, key=attrgetter('initial'), reverse=True)
        for state in states:
            for arc in state.arcs:
                itext = self.isyms.find(arc.ilabel)
                otext = self.osyms.find(arc.ilabel)
                txt_fst.write(
                    '{}\t{}\t{}\t{}\n'.format(
                        state.stateid,
                        arc.nextstate,
                        itext.encode('hex'),
                        otext.encode('hex')))
            if state.final:
                txt_fst.write('{}\n'.format(state.stateid))
        txt_fst.close()

    def load(self, txt_fst_filename):
        """
        Save the transducer in the text file format of OpenFST.
        The format is specified as follows:
            arc format: src dest ilabel olabel [weight]
            final state format: state [weight]
        lines may occur in any order except initial state must be first line
        Args:
            txt_fst_filename (string): The name of the file
        Returns:
            None
        """
        with open(txt_fst_filename, 'r') as txt_fst:
            for line in txt_fst:
                line = line.strip()
                splitted_line = line.split()
                if len(splitted_line) == 1:
                    self[int(splitted_line[0])].final = True
                else:
                    self.add_arc(int(splitted_line[0]), int(
                        splitted_line[1]), splitted_line[2].decode('hex'))

