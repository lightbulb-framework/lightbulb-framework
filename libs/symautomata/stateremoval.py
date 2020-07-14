"""
This module transforms a pyfst DFA to regular expressions
using the State Removal Method
"""
from sys import argv
from operator import attrgetter
from alphabet import createalphabet
from dfa import DFA
from flex2fst import Flexparser


class StateRemoval:
    """Transforms a pyfst DFA to regular expressions"""
    def __init__(self, input_fst_a, alphabet=None):
        """
        Args:
            input_fst_a (DFA): The DFA states
            alphabet (list): the input alphabet
        Returns:
            None
        """
        if alphabet is None:
            alphabet = createalphabet()
        self.mma = DFA(self.alphabet)
        self.mma.init_from_acceptor(input_fst_a)
        self.alphabet = alphabet

        self.l_transitions = {}
        self.epsilon = ''
        self.empty = None

    def star(self, input_string):
        """
        Kleene star operation
        Args:
            input_string (str): The string that the kleene star will be made
        Returns:
            str: The applied Kleene star operation on the input string
        """
        if input_string != self.epsilon and input_string != self.empty:
            return "(" + input_string + ")*"
        else:
            return ""

    def _state_removal_init(self):
        """State Removal Operation Initialization"""
        # First, we remove all multi-edges:
        for state_i in self.mma.states:
            for state_j in self.mma.states:
                if state_i.stateid == state_j.stateid:
                    self.l_transitions[
                        state_i.stateid, state_j.stateid] = self.epsilon
                else:
                    self.l_transitions[
                        state_i.stateid, state_j.stateid] = self.empty

                for arc in state_i.arcs:
                    if arc.nextstate == state_j.stateid:
                        if self.l_transitions[state_i.stateid, state_j.stateid] != self.empty:
                            self.l_transitions[state_i.stateid, state_j.stateid] \
                                += self.mma.isyms.find(arc.ilabel)
                        else:
                            self.l_transitions[state_i.stateid, state_j.stateid] = \
                                self.mma.isyms.find(arc.ilabel)

    def _state_removal_remove(self, k):
        """
        State Removal Remove operation
        l_transitions[i,i] += l_transitions[i,k] . star(l_transitions[k,k]) . l_transitions[k,i]
        l_transitions[j,j] += l_transitions[j,k] . star(l_transitions[k,k]) . l_transitions[k,j]
        l_transitions[i,j] += l_transitions[i,k] . star(l_transitions[k,k]) . l_transitions[k,j]
        l_transitions[j,i] += l_transitions[j,k] . star(l_transitions[k,k]) . l_transitions[k,i]
        Args:
            k (int): The node that will be removed
        Returns:
            None
        """
        for state_i in self.mma.states:
            for state_j in self.mma.states:
                if self.l_transitions[state_i.stateid, k] != self.empty:
                    l_ik = self.l_transitions[state_i.stateid, k]
                else:
                    l_ik = ""
                if self.l_transitions[state_j.stateid, k] != self.empty:
                    l_jk = self.l_transitions[state_j.stateid, k]
                else:
                    l_jk = ""
                if self.l_transitions[k, state_i.stateid] != self.empty:
                    l_ki = self.l_transitions[k, state_i.stateid]
                else:
                    l_ki = ""
                if self.l_transitions[k, state_j.stateid] != self.empty:
                    l_kj = self.l_transitions[k, state_j.stateid]
                else:
                    l_kj = ""

                if self.l_transitions[state_i.stateid, state_i.stateid] != self.empty:
                    self.l_transitions[state_i.stateid, state_i.stateid] += l_ik + \
                        self.star(self.l_transitions[k, k]) + l_ki
                else:
                    self.l_transitions[state_i.stateid, state_i.stateid] = l_ik + \
                        self.star(self.l_transitions[k, k]) + l_ki

                if self.l_transitions[state_j.stateid, state_j.stateid] != self.empty:
                    self.l_transitions[state_j.stateid, state_j.stateid] += l_jk + \
                        self.star(self.l_transitions[k, k]) + l_kj
                else:
                    self.l_transitions[state_j.stateid, state_j.stateid] = l_jk + \
                        self.star(self.l_transitions[k, k]) + l_kj

                if self.l_transitions[state_i.stateid, state_j.stateid] != self.empty:
                    self.l_transitions[state_i.stateid, state_j.stateid] += l_ik + \
                        self.star(self.l_transitions[k, k]) + l_kj
                else:
                    self.l_transitions[state_i.stateid, state_j.stateid] = l_ik + \
                        self.star(self.l_transitions[k, k]) + l_kj

                if self.l_transitions[state_j.stateid, state_i.stateid] != self.empty:
                    self.l_transitions[state_j.stateid, state_i.stateid] += l_jk + \
                        self.star(self.l_transitions[k, k]) + l_ki
                else:
                    self.l_transitions[state_j.stateid, state_i.stateid] = l_jk + \
                        self.star(self.l_transitions[k, k]) + l_ki

    def _state_removal_solve(self):
        """The State Removal Operation"""
        initial = sorted(
            self.mma.states,
            key=attrgetter('initial'),
            reverse=True)[0].stateid
        for state_k in self.mma.states:
            if state_k.final:
                continue
            if state_k.stateid == initial:
                continue
            self._state_removal_remove(state_k.stateid)

        print self.l_transitions
        return self.l_transitions

    def get_regex(self):
        """Regular Expression Generation"""
        self._state_removal_init()
        self._state_removal_solve()
        return self.l_transitions[0]


def main():
    """Testing function for DFA _Brzozowski Operation"""
    if len(argv) < 2:
        targetfile = 'target.y'
    else:
        targetfile = argv[1]
    print 'Parsing ruleset: ' + targetfile,
    flex_a = Flexparser()
    mma = flex_a.yyparse(targetfile)
    print 'OK'
    print 'Perform minimization on initial automaton:',
    mma.minimize()
    print 'OK'
    print 'Perform StateRemoval on minimal automaton:',
    state_removal = StateRemoval(mma)
    mma_regex = state_removal.get_regex()
    print mma_regex

if __name__ == '__main__':
    main()