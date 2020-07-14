"""This module contains the DFA implementation"""
# !/usr/bin/python
import imp
import copy
from alphabet import createalphabet
from operator import attrgetter

def bfs(graph, start):
    """
    Finds the shortest string using BFS
    Args:
        graph (DFA): The DFA states
        start (DFA state): The DFA initial state
    Returns:
        str: The shortest string
    """
    # maintain a queue of paths
    queue = []
    visited = []
    # maintain a queue of nodes
    # push the first path into the queue
    queue.append([['', start]])
    while queue:
        # get the first path from the queue
        path = queue.pop(0)
        # get the last node from the path
        node = path[-1][1]
        if node.stateid not in visited:
            visited.append(node.stateid)
            # path found
            if node.final != TropicalWeight(float('inf')):
                return "".join([mnode[0] for mnode in path])
            # enumerate all adjacent nodes, construct a new path and push
            # it into the queue
            for arc in node.arcs:
                char = graph.isyms.find(arc.ilabel)
                next_state = graph[arc.nextstate]
                # print next_state.stateid
                if next_state.stateid not in visited:
                    new_path = list(path)
                    new_path.append([char, next_state])
                    queue.append(new_path)


try:
    print 'Checking for pywrapfst module:',
    imp.find_module('pywrapfst')
    print 'OK'
    from pywrapfstdfa import PywrapfstDFA, TropicalWeight
    import pywrapfst as fst


    class DFA(PywrapfstDFA):
        """The DFA class implemented using openFst library"""

        def __init__(self, alphabet=createalphabet()):
            self.alphabet = alphabet
            super(DFA, self).__init__(alphabet)

        def copy(self):
            mma = DFA(self.alphabet)
            mma.automaton = self.automaton.copy()
            mma.alphabet = copy.deepcopy(self.alphabet)
            mma.isyms = copy.deepcopy(self.isyms)
            mma.osyms = copy.deepcopy(self.osyms)
            return mma

        def shortest_string(self):
            """
            Uses BFS in order to find the shortest string
            Args:
                None
            Returns:
                str: The shortest string
            """
            initialstates = sorted(
                self.states,
                key=attrgetter('initial'),
                reverse=True)
            if len(initialstates) > 0:
                return bfs(self, initialstates[0])
            else:
                return None

        def diff(self, input_mm):
            """
            Automata Diff operation
            """
            mma = DFA(self.alphabet)
            mma.init_from_acceptor(self)
            mmb = DFA(self.alphabet)
            mmb.init_from_acceptor(input_mm)
            mma.minimize()
            mmb.complement(self.alphabet)
            mmb.minimize()
            mmc = DFA(self.alphabet)
            mmc.init_from_acceptor(mma & mmb)
            return mmc

        def to_regex(self):
            """
            Returns a regex approximation
            Args:
                None
            Returns:
                str: A regex approximation
            """
            from regex import Regex
            converter = Regex(self)
            return converter.get_regex()

except ImportError:
    print 'FAIL'
    try:
        print 'Checking for fst module:',
        imp.find_module('fst')
        print 'OK'
        from fstdfa import FstDFA, TropicalWeight


        class DFA(FstDFA):
            """The DFA class implemented using openFst library"""
            def __init__(self, alphabet = createalphabet()):
                self.alphabet = alphabet
                super(DFA, self).__init__(alphabet)

            def shortest_string(self):
                """
                Uses BFS in order to find the shortest string
                Args:
                    None
                Returns:
                    str: The shortest string
                """
                initialstates = sorted(
                    self.states,
                    key=attrgetter('initial'),
                    reverse=True)
                if len(initialstates) > 0:
                    return bfs(self, initialstates[0])
                else:
                    return None

            def diff(self, input_mm):
                """
                Automata Diff operation
                """
                mma = DFA(self.alphabet)
                mma.init_from_acceptor(self)
                mmb = DFA(self.alphabet)
                mmb.init_from_acceptor(input_mm)
                mma.minimize()
                mmb.complement(self.alphabet)
                mmb.minimize()
                mmc = DFA(self.alphabet)
                mmc.init_from_acceptor(mma & mmb)
                return mmc

            def to_regex(self):
                """
                Returns a regex approximation
                Args:
                    None
                Returns:
                    str: A regex approximation
                """
                from regex import Regex
                converter = Regex(self)
                return converter.get_regex()

    except ImportError:
        print 'FAIL'
        print 'Fallback to python implementation:OK'
        from pythondfa import PythonDFA, TropicalWeight

        class DFA(PythonDFA):
            """The DFA class implemented using python"""

            def __init__(self, alphabet = createalphabet()):
                self.alphabet = alphabet
                super(DFA, self).__init__(alphabet)

            def copy(self):
                mma = DFA(self.alphabet)
                mma.states = copy.deepcopy(self.states)
                mma.alphabet = copy.deepcopy(self.alphabet)
                mma.isyms = copy.deepcopy(self.isyms)
                mma.osyms = copy.deepcopy(self.osyms)
                return mma

            def shortest_string(self):
                """
                Uses BFS in order to find the shortest string
                Args:
                    None
                Returns:
                    str: The shortest string
                """
                initialstates = sorted(
                    self.states,
                    key=attrgetter('initial'),
                    reverse=True)
                if len(initialstates) > 0:
                    return bfs(self, initialstates[0])
                else:
                    return None

            def diff(self, input_mm):
                """
                Automata Diff operation
                """
                mma = DFA(self.alphabet)
                mma.init_from_acceptor(self)
                mmb = DFA(self.alphabet)
                mmb.init_from_acceptor(input_mm)
                mma.minimize()
                mmb.complement(self.alphabet)
                mmb.minimize()
                mmc = DFA(self.alphabet)
                mmc.init_from_acceptor(mma & mmb)
                return mmc

            def to_regex(self):
                """
                Returns a regex approximation
                Args:
                    None
                Returns:
                    str: A regex approximation
                """
                from regex import Regex
                converter = Regex(self)
                return converter.get_regex()
