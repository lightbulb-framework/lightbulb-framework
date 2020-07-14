"""
This module transforms a pyfst DFA to regular expressions
using the Brzozowski Algebraic Method
"""
import sys
from collections import OrderedDict
from operator import attrgetter

from alphabet import createalphabet
from dfa import DFA
from flex2fst import Flexparser


class Brzozowski:
    """
    This class transforms a pyfst DFA to regular expressions
    using the Brzozowski Algebraic Method
    """

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
        self.alphabet = alphabet
        self.mma = DFA(self.alphabet)
        self.mma.init_from_acceptor(input_fst_a)
        # a is a matrix that holds all transitions
        # If there is a transition from state 0 to state 1 with the symbol x
        # then a[0][1]=x
        self.A = {}
        # B[n] holds the regular expression that describes how a final state
        # can be reached from state n
        self.B = {}
        self.epsilon = ''
        self.empty = None

    def _bfs_sort(self, start):
        """
        maintain a map of states distance using BFS
        Args:
            start (fst state): The initial DFA state
        Returns:
            list: An ordered list of DFA states
                  using path distance
        """
        pathstates = {}
        # maintain a queue of nodes to be visited. Both current and previous
        # node must be included.
        queue = []
        # push the first path into the queue
        queue.append([0, start])
        pathstates[start.stateid] = 0
        while queue:
            # get the first node from the queue
            leaf = queue.pop(0)
            node = leaf[1]
            pathlen = leaf[0]
            # enumerate all adjacent nodes, construct a new path and push it
            # into the queue
            for arc in node.arcs:
                next_state = self.mma[arc.nextstate]
                if next_state.stateid not in pathstates:
                    queue.append([pathlen + 1, next_state])
                    pathstates[next_state.stateid] = pathlen + 1
        orderedstatesdict = OrderedDict(
            sorted(
                pathstates.items(),
                key=lambda x: x[1],
                reverse=False))
        for state in self.mma.states:
            orderedstatesdict[state.stateid] = state
        orderedstates = [x[1] for x in list(orderedstatesdict.items())]
        return orderedstates

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

    def _brzozowski_algebraic_method_init(self):
        """Initialize Brzozowski Algebraic Method"""
        # Initialize B
        for state_a in self.mma.states:
            if state_a.final:
                self.B[state_a.stateid] = self.epsilon
            else:
                self.B[state_a.stateid] = self.empty
            # Initialize A
            for state_b in self.mma.states:
                self.A[state_a.stateid, state_b.stateid] = self.empty
                for arc in state_a.arcs:
                    if arc.nextstate == state_b.stateid:
                        self.A[state_a.stateid, state_b.stateid] = \
                            self.mma.isyms.find(arc.ilabel)

    def _brzozowski_algebraic_method_solve(self):
        """Perform Brzozowski Algebraic Method"""
        orderedstates = self._bfs_sort(
            sorted(
                self.mma.states,
                key=attrgetter('initial'),
                reverse=True)[0])
        for n in range(len(orderedstates) - 1, 0, -1):
            # print "n:" + repr(n)
            if self.A[
                    orderedstates[n].stateid,
                    orderedstates[n].stateid] != self.empty:
                # B[n] := star(A[n,n]) . B[n]
                if self.B[orderedstates[n].stateid] != self.empty:
                    self.B[orderedstates[n].stateid] = \
                        self.star(self.A[orderedstates[n].stateid, orderedstates[n].stateid]) \
                        + self.B[orderedstates[n].stateid]
                else:
                    self.B[orderedstates[n].stateid] = self.star(
                        self.A[orderedstates[n].stateid, orderedstates[n].stateid])
                for j in range(0, n):
                    # A[n,j] := star(A[n,n]) . A[n,j]
                    if self.A[
                            orderedstates[n].stateid,
                            orderedstates[j].stateid] != self.empty:
                        self.A[
                            orderedstates[n].stateid,
                            orderedstates[j].stateid] = \
                            self.star(self.A[orderedstates[n].stateid, orderedstates[n].stateid]) \
                            + self.A[orderedstates[n].stateid, orderedstates[j].stateid]
                    else:
                        self.A[orderedstates[n].stateid, orderedstates[j].stateid] = self.star(
                            self.A[orderedstates[n].stateid, orderedstates[n].stateid])
            for i in range(0, n):
                # B[i] += A[i,n] . B[n]
                newnode = None
                if self.A[orderedstates[i].stateid, orderedstates[n].stateid] != self.empty \
                        and self.B[orderedstates[n].stateid] != self.empty:
                    newnode = self.A[orderedstates[i].stateid, orderedstates[
                        n].stateid] + self.B[orderedstates[n].stateid]
                elif self.A[orderedstates[i].stateid, orderedstates[n].stateid] != self.empty:
                    newnode = self.A[
                        orderedstates[i].stateid,
                        orderedstates[n].stateid]
                elif self.B[orderedstates[n].stateid] != self.empty:
                    newnode = self.B[orderedstates[n].stateid]
                if self.B[orderedstates[i].stateid] != self.empty:
                    if newnode is not None:
                        self.B[orderedstates[i].stateid] += newnode
                else:
                    self.B[orderedstates[i].stateid] = newnode
                for j in range(0, n):
                    # A[i,j] += A[i,n] . A[n,j]
                    newnode = None
                    if self.A[
                            orderedstates[i].stateid,
                            orderedstates[n].stateid] != self.empty \
                            and self.A[orderedstates[n].stateid, orderedstates[j].stateid] \
                                    != self.empty:
                        newnode = self.A[orderedstates[i].stateid, orderedstates[
                            n].stateid] + self.A[orderedstates[n].stateid, orderedstates[j].stateid]
                    elif self.A[orderedstates[i].stateid, orderedstates[n].stateid] != self.empty:
                        newnode = self.A[
                            orderedstates[i].stateid,
                            orderedstates[n].stateid]
                    elif self.A[orderedstates[n].stateid, orderedstates[j].stateid] != self.empty:
                        newnode = self.A[
                            orderedstates[n].stateid,
                            orderedstates[j].stateid]
                    if self.A[
                            orderedstates[i].stateid,
                            orderedstates[j].stateid] != self.empty:
                        if newnode is not None:
                            self.A[
                                orderedstates[i].stateid,
                                orderedstates[j].stateid] += newnode
                    else:
                        self.A[
                            orderedstates[i].stateid,
                            orderedstates[j].stateid] = newnode


    def get_regex(self):
        """Generate regular expressions from DFA automaton"""
        self._brzozowski_algebraic_method_init()
        self._brzozowski_algebraic_method_solve()
        return self.B


def main():
    """
    Testing function for DFA brzozowski algebraic method Operation
    """
    argv = sys.argv
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
    print 'Perform Brzozowski on minimal automaton:',
    brzozowski_a = Brzozowski(mma)
    mma_regex = brzozowski_a.get_regex()
    print mma_regex

if __name__ == '__main__':
    main()
