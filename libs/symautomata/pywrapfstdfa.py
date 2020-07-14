"""
This module encapsulates the interface to OpenFST. This
module depends on OpenFST. To enable Python support in OpenFST, use a
recent version (>=1.5.2) and compile with ``--enable_python``.
Further information can be found here:

http://www.openfst.org/twiki/bin/view/FST/PythonExtension

"""
#!/usr/bin/python
from operator import attrgetter
from alphabet import createalphabet
EPSILON = 0xffff
import pywrapfst as fst

def TropicalWeight(param):
    """
    Returns the emulated fst TropicalWeight
    Args:
        param (str): The input
    Returns:
        bool: The arc weight
    """
    if param == (float('inf')):
        return False
    else:
        return True

class DFAArc:
    """The DFA transition"""

    def __init__(self, srcstate_id, nextstate_id, ilabel=None):
        """
        The initialization function
        Args:
            srcstate_id (int): The source state identifier
            nextstate_id (int): The destination state identifier
            ilabel (str): The symbol corresponding to character for the transition
        """
        self.srcstate = srcstate_id
        self.nextstate = nextstate_id
        self.ilabel = ilabel


class DFAState(object):
    """The DFA statess"""

    def __init__(self, cur_fst, cur_node):
        """
        Initialization function
        Args:
            sid (int): The state identifier
        Returns:
            None
        """
        self.cur_node = cur_node
        self.cur_fst = cur_fst


    def __iter__(self):
        """Iterator"""
        return iter(self.cur_fst.arcs(self.cur_node))

    def __getattribute__(self, x):
        if x == 'arcs':
            arcs = self.cur_fst.arcs(self.cur_node)
            return [DFAArc(self.cur_node, arc.nextstate, arc.ilabel) for arc in arcs]
        if x == 'stateid':
            return self.cur_node
        if x == 'initial':
            return self.cur_fst.start == self.cur_node
        if x == 'final':
            return self.cur_fst.final(self.cur_node) == fst.Weight.One(self.cur_fst.weight_type())
        return object.__getattribute__(self, x)



    def __setattr__(self, x, value):
        if x == 'arcs':
            print  'Setting arcs is not implemented'
            exit(1)
        if x == 'stateid':
            print  'Setting statedid is not implemented'
            exit(1)
        if x == 'initial':
            if value == True:
                self.cur_fst.set_start(self.cur_node)
            else:
                print  'Unsetting start is not implemented'
                exit(1)
        if x == 'final':
            if value == True:
                self.cur_fst.set_final(self.cur_node)
            else:
                self.cur_fst.set_final(self.cur_node, fst.Weight.Zero(self.cur_fst.weight_type()))
        return object.__setattr__(self, x, value)



class syms:
    """The DFA accepted symbols"""
    symbols = None
    reversesymbols = None

    def __init__(self):
        """Initialize symbols"""
        self.symbols = {}
        self.reversesymbols = {}

    def __getitem__(self, char):
        """
        Finds a symbol identifier based on the input character
        Args:
            char (str): The symbol character
        Returns:
            int: The retrieved symbol identifier
        """
        return self.reversesymbols[char]

    def __setitem__(self, char, num):
        """
        Sets a symb
        Sets a symbol
        Args:
            char (str): The symbol character
            num (int): The  symbol identifier
        Returns:
           None
        """
        self.symbols[num] = char
        self.reversesymbols[char] = num

    def find(self, num):
        """
        Finds a symbol based on its identifier
        Args:
            num (int): The symbol identifier
        Returns:
            str: The retrieved symbol
        """
        return self.symbols[num]

    def items(self):
        """Returns all stored symbols
        Args:
            None
        Returns:
            dict:The included symbols
        """
        return self.symbols


class PywrapfstDFA(object):
    """A DFA implementation that uses the
    same interface with python symautomata"""
    def __init__(self, alphabet=createalphabet()):
        """
        Args:
            alphabet (list): The imput alphabet
        Returns:
            None
        """
        self.automaton = fst.Fst()
        id = self.add_state()
        self.automaton.set_start(id)
        self.alphabet = alphabet
        num = 1
        self.isyms = syms()
        self.osyms = syms()
        insymbols = fst.SymbolTable()
        outsymbols = fst.SymbolTable()
        for char in alphabet:
             self.isyms.__setitem__(char, num)
             self.osyms.__setitem__(char, num)
             insymbols.add_symbol(char, num)
             outsymbols.add_symbol(char, num)
             num = num + 1
        self.automaton.set_input_symbols(insymbols)
        self.automaton.set_output_symbols(outsymbols)




    def __str__(self):
        """Describes DFA object"""
        return "This is a pywrapfstDFA object with " + `len(self.states)` + " states"

    def __getattribute__(self, x):
        if x == 'states':
            return [DFAState(self.automaton, state) for state in self.automaton.states()]
        return object.__getattribute__(self, x)



    def __getitem__(self, id):
        """
        Retrieves a state
        Args:
            state (int): State identifier
        Returns:
            DFA state: The selected dfa state
        """
        allocatedstate = DFAState(self.automaton, id)
        return allocatedstate


    def add_state(self):
        """Adds a new state"""
        return self.automaton.add_state()


    def add_arc(self, src, dst, char):
        """Adds a new Arc
        Args:
            src (int): The source state identifier
            dst (int): The destination state identifier
            char (str): The character for the transition
        Returns:
            None
        """
        if src not in self.automaton.states():
            self.add_state()
        arc = fst.Arc(self.isyms[char], self.osyms[char],  fst.Weight.One(self.automaton.weight_type()), dst)
        self.automaton.add_arc(src, arc)


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

        insymbols = fst.SymbolTable()
        outsymbols = fst.SymbolTable()
        num = 1
        for char in self.alphabet:
            self.isyms.__setitem__(char, num)
            self.osyms.__setitem__(char, num)
            insymbols.add_symbol(char, num)
            outsymbols.add_symbol(char, num)
            num = num + 1
        self.automaton.set_input_symbols(insymbols)
        self.automaton.set_output_symbols(outsymbols)
        endstate = self.add_state()
        for state in self.states:
            for char in alphabet:
                found = 0
                for arc in state.arcs:
                    if self.isyms.find(arc.ilabel) == char:
                        found = 1
                        break
                if found == 0:
                    self.add_arc(state.stateid, endstate, char)
        self[endstate].final = False

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
        endstate = self.add_state()
        for state in self.states:
            for char in alphabet:
                found = 0
                for arc in state.arcs:
                    if self.isyms.find(arc.ilabel) == char:
                        found = 1
                        break
                if found == 0:
                    self.add_arc(state.stateid, endstate, char)

        self[endstate].final = False

        for char in alphabet:
            self.add_arc(endstate, endstate, char)
        self.determinize()

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
        return cur_state.final

    def empty(self):
        """
        Return True if the DFA accepts the empty language.
        """
        # self.minimize()
        return len(list(self.states)) == 0

    def complement(self, alphabet):
        """
        Returns the complement of DFA
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        self._addsink(alphabet)
        for state in self.automaton.states():
            if self.automaton.final(state) == fst.Weight.One(self.automaton.weight_type()):
                self.automaton.set_final(state, fst.Weight.Zero(self.automaton.weight_type()))
            else:
                self.automaton.set_final(state, fst.Weight.One(self.automaton.weight_type()))


    def init_from_acceptor(self, acceptor):
        """
        Adds a sink state
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        self.automaton = acceptor.automaton

    def init_from_acceptor_bycopying(self, acceptor):
        """
        Adds a sink state
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        for state in acceptor.states:
            for arc in state.arcs:
                self.add_arc(state.stateid, arc.nextstate, acceptor.isyms.find(arc.ilabel))
            if state.final:
                print state.stateid,' is final'
                self[state.stateid].final = True;


    def save(self, txt_fst_file_name):
        """
        Save the machine in the openFST format in the file denoted by
        txt_fst_file_name.
        Args:
            txt_fst_file_name (str): The output file
        Returns:
            None
        """
        output_filename = open(txt_fst_file_name, 'w+')
        states = sorted(self.states, key=attrgetter('initial'), reverse=True)
        for state in states:
            for arc in state.arcs:
                if arc.ilabel == 0:
                    continue
                itext = self.isyms.find(arc.ilabel)
                otext = self.osyms.find(arc.ilabel)
                output_filename.write(
                    '{}\t{}\t{}\t{}\n'.format(
                        state.stateid,
                        arc.nextstate,
                        itext.encode('hex'),
                        otext.encode('hex')))
            if state.final:
                output_filename.write('{}\n'.format(state.stateid))
        output_filename.close()

    def load(self, txt_fst_file_name):
        """
        Save the transducer in the text file format of OpenFST.
        The format is specified as follows:
            arc format: src dest ilabel olabel [weight]
            final state format: state [weight]
        lines may occur in any order except initial state must be first line
        Args:
            txt_fst_file_name (str): The input file
        Returns:
            None
        """
        with open(txt_fst_file_name, 'r') as input_filename:
            for line in input_filename:
                line = line.strip()
                split_line = line.split()
                if len(split_line) == 1:
                    self[int(split_line[0])].final = True
                else:
                    if int(split_line[1]) == 0:
                        continue
                    self.add_arc(int(split_line[0]), int(split_line[1]),
                                 split_line[2].decode('hex'))


    def minimize(self):
        """Minimizes the DFA using Hopcroft algorithm"""
        self.determinize()
        self.automaton.minimize()
        #self._addsink(self.alphabet)

    def intersect(self, other):
        """Constructs an unminimized DFA recognizing
        the intersection of the languages of two given DFAs.
        Args:
            other (DFA): The other DFA that will be used
                         for the intersect operation
        Returns:
        Returns:
            DFA: The resulting DFA
        """
        self.automaton = fst.intersect(self.automaton, other.automaton)
        return  self

    def __and__(self, other):
        """Constructs an unminimized DFA recognizing
               the intersection of the languages of two given DFAs.
               Args:
                   other (DFA): The other DFA that will be used
                                for the intersect operation
               Returns:
                   DFA: The resulting DFA
               """
        self.intersect(other)
        return self

    def symmetric_difference(self, other):
        """Constructs an unminimized DFA recognizing
        the symmetric difference of the languages of two given DFAs.
        Args:
            other (DFA): The other DFA that will be used
                         for the symmetric difference operation
        Returns:
            DFA: The resulting DFA
        """
        self.automaton.symmetric_difference(other)
        return  self

    def union(self, other):
        """Constructs an unminimized DFA recognizing the union of the languages of two given DFAs.
        Args:
            other (DFA): The other DFA that will be used
                         for the union operation
        Returns:
            DFA: The resulting DFA
        """
        self.automaton.union(other.automaton)
        return self

    def __or__(self, other):
        """Constructs an unminimized DFA recognizing the union of the languages of two given DFAs.
                Args:
                    other (DFA): The other DFA that will be used
                                 for the union operation
                Returns:
                    DFA: The resulting DFA
                """
        self.union(other)
        return self

    def determinize(self):
        """
        Transforms a Non Deterministic DFA into a Deterministic
        Args:
            None
        Returns:
            DFA: The resulting DFA
        """
        # This function is not necessary
        self.automaton = fst.determinize(self.automaton)
        return  self

    def invert(self):
        """Inverts the DFA final states"""
        self.automaton.invert()

    def difference(self, other):
        """Performs the Diff operation between two atomata
        Args:
            other (DFA): The other DFA that will be used
                         for the difference operation
        Returns:
            DFA: The resulting DFA
        """
        other.invert()
        self.intersect(other)
        return self

    def __sub__(self, other):
        """Performs the Diff operation between two atomata
        Args:
            other (DFA): The other DFA that will be used
                        for the difference operation
        Returns:
            DFA: The resulting DFA
        """
        self.difference(other)
        return self


