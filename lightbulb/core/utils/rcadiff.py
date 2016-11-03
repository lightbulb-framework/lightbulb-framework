"""This module performs RCADiff operation"""
from sys import argv
from itertools import product
from symautomata.dfa import DFA
from symautomata.alphabet import createalphabet
from symautomata.flex2fst import Flexparser

def rca_diff_dev(dfa1, dfa2, alphabet, num_diff = 1, dfa1_minus_dfa2 = False):
    """
    Compute the set of root cause differences and return
    """

    def _get_state_neighbors(dfa, sid):
        """
        return a tuple (state, symbol) for all states that can be accesed by one
        transition from the input state.
        """
        neighbors = []
        n_set = set([])
        for arc in dfa[sid].arcs:
            dst_id = arc.nextstate
            symbol = dfa.isyms.find(arc.ilabel)
            if dst_id in n_set or dst_id == sid:
                continue
            n_set.add(dst_id)
            neighbors.append((dst_id, symbol))
        return neighbors


    def _get_path_dfs(dfa, src_id, dst_id, visited, differences, current_input):
        """
        Return an input for every simple path from src_id to dst_id in dfa given
        that we already have visited the "visited" states and have an input of
        current_input. The resulting differences found are stored in the respective
        argument variable.
        """

        if src_id == dst_id:
            differences.append(''.join(current_input))
            return

        neighbors = _get_state_neighbors(dfa, src_id)
        for (sid, symbol) in neighbors:
            if sid in visited:
                continue
            visited.append(sid)
            current_input.append(symbol)
            _get_path_dfs(dfa, sid, dst_id, visited, differences, current_input)
            if len(differences) == num_diff:
                return
            visited.pop()
            current_input.pop()



    def _get_simple_paths_input(dfa, target_state_id):
        """
        Return inputs exercising all paths from the initial state to the target
        state.
        """

        differences = []
        visited = [0]
        current_input = []

        # For each state get a set of pairs (state, symbol) where symbol is taking
        # us to the state "state".
        neighbors = _get_state_neighbors(dfa, 0)

        for (sid, symbol) in neighbors:
            visited.append(sid)
            current_input.append(symbol)
            _get_path_dfs(dfa, sid, target_state_id, visited,
                          differences, current_input)
            if len(differences) == num_diff:
                return []
            visited.pop()
            current_input.pop()
        return differences

    # # #  # # #  # # #  # # #  # # #
    # _rca_diff code starts here #
    #

    prod_dfa = DFA(alphabet)

    # This will give us the id of the state in the product DFA.
    get_state = lambda sid1, sid2, len2: sid1 * len2 + sid2

    # Points of exposure is a subset of the non accepting states in the
    # product automaton
    poe = []

    for (s1, s2) in product(dfa1.states, dfa2.states):
        src_id = get_state(s1.stateid, s2.stateid, len(dfa2))
        t1 = { dfa1.isyms.find(arc.ilabel): arc.nextstate for arc in s1 }
        t2 = { dfa2.isyms.find(arc.ilabel): arc.nextstate for arc in s2 }
        for char in alphabet:
            dst_id = get_state(t1[char], t2[char],
                               len(dfa2))
            prod_dfa.add_arc(src_id, dst_id, char)

        prod_dfa[src_id].final = s1.final and s2.final
        if (dfa1_minus_dfa2 and s1.final and not s2.final) or \
                (not dfa1_minus_dfa2 and s1.final != s2.final):
            poe.append(src_id)


    # Product DFA is ready. Iterate with a DFS to get all paths to the points
    # of exposure
    differences = [None]
    for sid in poe:
        differences += _get_simple_paths_input(prod_dfa, sid)
        if len(differences) == num_diff:
            break
    return differences

def rca_diff(dfa_a, dfa_b, alphabet, num_diff = 1, dfa1_minus_dfa2 = False):
    """
    Args:
        dfa1 (DFA): The fist DFA
        dfa2 (DFA): The SECOND DFA
        alphabet (list): The input alphabet
        left (boolean): Perform the Diff mma - mmb
        right (boolean): Perform the Diff mmb - mma
    Returns:
        None
    """
    if alphabet is None:
        alphabet = createalphabet()

    dfa1 = DFA(alphabet)
    dfa1.init_from_acceptor(dfa_a)
    dfa2 = DFA(alphabet)
    dfa2.init_from_acceptor(dfa_b)
    """
    Execute algorithm
    """
    counterexamples = []
    mmc = dfa1.diff(dfa2)
    counterexample = mmc.shortest_string()
    counterexamples.append(counterexample)
    if not dfa1_minus_dfa2:
        mmc = dfa2.diff(dfa1)
        counterexample = mmc.shortest_string()
        counterexamples.append(counterexample)
    return counterexamples


