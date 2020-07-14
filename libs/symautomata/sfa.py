"""
This module performs all basic SFA operations.
It is an interface for sfa automata.
"""
# !/usr/bin/python
import random
import string

from dfa import DFA


class Predicate:
    """
    The predicate statement
    """

    def __init__(self, initializer):
        """
        This __init__ method is not implemented
        """
        raise NotImplementedError('__init__ method not implemented')

    def is_sat(self, symbol):
        """
        This is_sat method is not implemented
        """
        raise NotImplementedError('is_sat method not implemented')

    def refactor(self, symbol, value):
        """
        This refactor method is not implemented
        """
        raise NotImplementedError('refactor method not implemented')

    def get_witness(self):
        """
        This get_witness method is not implemented
        """
        raise NotImplementedError('get_witness method not implemented')

    def __iter__(self):
        """
        This __iter__ method is not implemented
        """
        raise NotImplementedError('__iter__ method not implemented')


class SetPredicate(Predicate):
    """
    This class initializes and sets a predicate for the
    current transition
    """

    def __init__(self, initializer):
        """
        Initialization Function
        Args:
            initializer (list): A list of characters
        Returns:
            None
        """
        self.pset = set(initializer)

    def is_sat(self, symbol):
        """
        Args:
            symbol:
        Returns:
            bool: The response can be true or false
        """
        return symbol in self.pset

    def refactor(self, symbol, value):
        """
        Args:
            symbol:
            value:
        Returns:
            None
        """
        if value:
            self.pset.add(symbol)
        else:
            self.pset.remove(symbol)

    def get_witness(self):
        """
        Args:
            None
        Returns:
            str: A random sample
        """
        return random.sample(self.pset, 1)[0]

    def __iter__(self):
        """
        Args:
            None
        Returns:
            None
        """
        return iter(self.pset)


class SFAState:
    """The SFA state structure"""
    def __init__(self, sid=None):
        """
        Args:
            sid (int): The state identifier
        Returns:
            None
        """
        self.final = False
        self.initial = False
        self.state_id = sid
        self.arcs = []

    def __iter__(self):
        """
        Args:
            None
        Returns:
            None
        """
        return iter(self.arcs)


class SFAArc:
    """The SFA Arc structure"""
    def __init__(self, src_state_id, dst_state_id, guard_p, term=None):
        """
        Initialization function for Arc's guardgen structure
        Args:
            src_state_id (int): The source state identifier
            dst_state_id (int): The destination state identifier
            guard_p: The input character
            term: The input term
        Returns:
            None
        """
        self.src_state = src_state_id
        self.dst_state = dst_state_id
        self.guard = guard_p
        self.term = None


class SFA:
    """
       Symbolic Finite Automata (SFAs) are finite state symautomata
       in which the alphabet is given by a Boolean algebra that may
       have an infinite domain, and transitions are labeled with
       first-order predicates over such algebra
    """

    def __init__(self, alphabet=None):
        """
        Initialization of the SFA oject
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        self.states = []
        self.arcs = []
        self.alphabet = alphabet

    def add_state(self):
        """This function adds a new state"""
        sid = len(self.states)
        self.states.append(SFAState(sid))

    def add_arc(self, src, dst, char):
        """
        This function adds a new arc in a SFA state
        Args:
            src (int): The source state identifier
            dst (int): The destination state identifier
            char (str): The transition symbol
        Returns:
            None
        """
        assert type(src) == type(int()) and type(dst) == type(int()), \
            "State type should be integer."
        while src >= len(self.states) or dst >= len(self.states):
            self.add_state()
        self.states[src].arcs.append(SFAArc(src, dst, char))

    def random_string(self, size=1):
        """
        This function generates a random string
        Args:
            size (int): The length of the random string
        Returns:
            str: A random string
        """
        pass

    def consume_input(self, inp):
        """
        Return True/False if the machine accepts/reject the input.
        Args:
            inp (str): input string to be consumed
        Retunrs:
            bool: A true or false value depending on if the DFA
                accepts the provided input
        """
        cur_state = self.states[0]
        for character in inp:
            found = False
            for arc in cur_state.arcs:
                if arc.guard.is_sat(character):
                    cur_state = self.states[arc.dst_state]
                    found = True
                    break

            if not found:
                raise RuntimeError('SFA not complete')

        return cur_state.final

    def concretize(self):
        """
        Transforms the SFA into a DFA
        Args:
            None
        Returns:
            DFA: The generated DFA
        """
        dfa = DFA(self.alphabet)
        for state in self.states:
            for arc in state.arcs:
                for char in arc.guard:
                    dfa.add_arc(arc.src_state, arc.dst_state, char)

        for i in xrange(len(self.states)):
            if self.states[i].final:
                dfa[i].final = True
        return dfa


    def save(self, txt_fst_filename):
        """
        Save the machine in the openFST format in the file denoted by
        txt_fst_filename.
        Args:
            txt_fst_filename (str): The name of the file
        Returns:
            None
        """
        dfa = self.concretize()
        return dfa.save(txt_fst_filename)


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
        raise NotImplementedError('SFA load method not implemented')




def main():
    """Main Function"""
    alphabet = list(string.lowercase)  # + ["<", ">"]

    # Create an SFA for the regular expression .*<t>.*
    sfa = SFA(alphabet)

    # sfa.add_arc(0,0,SetPredicate([ i for i in alphabet if i != "<" ]))
    # sfa.add_arc(0,1,SetPredicate(list("<")))
    #
    # sfa.add_arc(1,2,SetPredicate(list("t")))
    # sfa.add_arc(1,0,SetPredicate([ i for i in alphabet if i != "t" ]))
    #
    # sfa.add_arc(2,3,SetPredicate(list(">")))
    # sfa.add_arc(2,0,SetPredicate([ i for i in alphabet if i != ">" ]))
    #
    # sfa.add_arc(3,3,SetPredicate(alphabet))
    #
    # sfa.states[3].final = True

    sfa.add_arc(0, 7, SetPredicate([i for i in alphabet if i != "d" and i != "input_string"]))
    sfa.add_arc(1, 7, SetPredicate([i for i in alphabet if i != "i"]))
    sfa.add_arc(2, 7, SetPredicate([i for i in alphabet if i != "p"]))
    sfa.add_arc(3, 7, SetPredicate([i for i in alphabet if i != "v"]))
    sfa.add_arc(5, 7, SetPredicate(list(alphabet)))
    sfa.add_arc(4, 7, SetPredicate([i for i in alphabet if i != "a"]))
    sfa.add_arc(6, 7, SetPredicate([i for i in alphabet if i != "n"]))
    sfa.add_arc(7, 7, SetPredicate(list(alphabet)))

    sfa.add_arc(0, 1, SetPredicate(list("d")))
    sfa.add_arc(1, 3, SetPredicate(list("i")))
    sfa.add_arc(3, 5, SetPredicate(list("v")))

    sfa.add_arc(0, 2, SetPredicate(list("input_string")))
    sfa.add_arc(2, 4, SetPredicate(list("p")))
    sfa.add_arc(4, 6, SetPredicate(list("a")))
    sfa.add_arc(6, 5, SetPredicate(list("n")))

    sfa.states[5].final = True

    dfa = sfa.concretize()
    # dfa.minimize()
    dfa.save('concrete_re_sfa.dfa')

    # Consume some input
    input_string = "koukouroukou"
    print 'SFA-DFA result on {}: {} - {}'.format(input_string, sfa.consume_input(input_string),
                                                 dfa.consume_input(input_string))

    input_string = "divspan"
    print 'SFA-DFA result on {}: {} - {}'.format(input_string, sfa.consume_input(input_string),
                                                 dfa.consume_input(input_string))

    input_string = "div"
    print 'SFA-DFA result on {}: {} - {}'.format(input_string, sfa.consume_input(input_string),
                                                 dfa.consume_input(input_string))

    input_string = "span"
    print 'SFA-DFA result on {}: {} - {}'.format(input_string, sfa.consume_input(input_string),
                                                 dfa.consume_input(input_string))


if __name__ == '__main__':
    main()
