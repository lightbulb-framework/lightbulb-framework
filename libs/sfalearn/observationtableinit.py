"""This module initializes the observation table using an input atomaton"""
from collections import defaultdict
from operator import attrgetter
from symautomata.dfa import TropicalWeight
from symautomata.alphabet import createalphabet
from symautomata.dfa import DFA


class ObservationTableInit:
    """This class initializes the observation table"""
    epsilon = ''
    alphabet = []
    access_strings_map = []
    distinguishStringsMap = []
    bookkeeping = []

    def __init__(
            self,
            epsilon,
            alphabet=None):
        """
        Initialization Function
        Args:
            epsilon (str): The epsilon symbol
            alphabet (list): The DFA Alphabet
        Returns:
            None
        """
        self.bookeeping = None
        self.groups = None
        self.epsilon = epsilon
        if alphabet is None:
            alphabet = createalphabet()
        self.alphabet = alphabet

    def _bfs_path_states(self, graph, start):
        """
        Find state access strings (DFA shortest paths for every state)
        using BFS
        Args:
            graph (DFA): The DFA states
            start (int): The DFA initial state
        Return:
            list: A list of all the DFA shortest paths for every state
        """
        pathstates = {}
        # maintain a queue of paths
        queue = []
        visited = []
        # push the first path into the queue
        queue.append([['', start]])
        while queue:
            # get the first path from the queue
            path = queue.pop(0)
            # get the last node from the path
            node = path[-1][1]
            # path found """
            if node.stateid not in pathstates and node.stateid != len(list(graph.states)):
                pathstates[node.stateid] = ''.join(
                    [mnode[0] for mnode in path])
            visited.append(node.stateid)
            # enumerate all adjacent nodes, construct a new path and push it
            # into the queue
            for arc in node.arcs:
                char = graph.isyms.find(arc.ilabel)
                next_state = graph[arc.nextstate]
                if next_state.stateid not in visited:
                    new_path = list(path)
                    new_path.append([char, next_state])
                    queue.append(new_path)
        return pathstates

    def _delta(self, graph, cur_state, char):
        """
        Function describing the transitions
        Args:
            graph (DFA): The DFA states
            cur_state (DFA state): The DFA current state
            char (str):: The char that will be used for the transition
        Return:
            DFA Node: The next state
        """
        for arc in cur_state.arcs:
            if graph.isyms.find(arc.ilabel) == char:
                return graph[arc.nextstate]

    def _get_accepted(self, graph):
        """
        Find the accepted states
        Args:
            graph (DFA): The DFA states
        Return:
            list: Returns the list of the accepted states
        """
        accepted = []
        for state in graph.states:
            if state.final != TropicalWeight(float('inf')):
                accepted.append(state)
        return accepted

    def _object_set_to_state_list(self, objectset):
        """
        Args:
            objectset (list): A list of all the DFA states (as objects)
        Return:
            list: A list of all the DFA states (as identifiers)
        """
        state_list = []
        for state in list(objectset):
            state_list.append(state.stateid)
        return state_list

    def _get_group_from_state(self, sid):
        """
        Args:
            sid (int): The state identifier
        Return:
            int: The group identifier that the state belongs
        """
        for index, selectgroup in enumerate(self.groups):
            if sid in selectgroup:
                return index

    def _reverse_to_source(self, target, group1):
        """
        Args:
            target (dict): A table containing the reverse transitions for each state
            group1 (list): A group of states
        Return:
            Set: A set of states for which there is a transition with the states of the group
        """
        new_group = []
        for dst in group1:
            new_group += target[dst]
        return set(new_group)

    def _partition_group(self, group):
        """
        Args:
            group (list):  A group of states
        Return:
            tuple: A set of two groups
        """
        for (group1, group2, distinguish_string) in self.bookeeping:
            if group & group1 != set() and not group.issubset(group1):
                new_g1 = group & group1
                new_g2 = group - group1
                return (new_g1, new_g2, distinguish_string)
            if group & group2 != set() and not group.issubset(group2):
                new_g1 = group & group2
                new_g2 = group - group2
                return (new_g1, new_g2, distinguish_string)
        assert False, "Unmatched group partition"

    def _init_smi(self, graph, access_strings_map):
        """
        Args:
            graph (DFA): The DFA states
            access_strings_map (list): a dict containing all the access strings for each state
        Return:
            list: SMI transition table
        """
        smi = []
        for selected_state in sorted(graph.states, key=attrgetter('initial'), reverse=True):
            # Initially gather all transitions of the state into a dictionary
            transitions_map = defaultdict(list)
            for character in self.alphabet:
                destination_state = self._delta(graph, selected_state, character)
                transitions_map[destination_state.stateid].append(character)

            chars_in_smi = []
            sorted_transitions = sorted(
                transitions_map.items(),
                key=lambda x: len(
                    x[1]))

            if len(sorted_transitions) == 1:
                # Just put 1 symbol is enough all other'input_string will be generalized
                # by the guardgen algorithm
                chars_in_smi.append(self.alphabet[0])
            else:
                # Otherwise insert in smi_vector all transitions as explicit except
                # the one from the sink transition where we add just enough
                # explicity transitions to make sure that this state will be
                # selected as the sink state.
                #
                # If no transition has a clear advantage in terms of symbols then
                # just add all transitions in explicit form because it may be the
                # case the guardgen() will generalize in the wrong transition.
                for (_, char_list) in sorted_transitions[:-1]:
                    chars_in_smi += char_list

                sink_chars = len(sorted_transitions[-2][1]) + 1
                chars_in_smi.extend(sorted_transitions[-1][1][:sink_chars])

            access_string = access_strings_map[selected_state.stateid]
            smi.extend([access_string + character for character in chars_in_smi])
        return smi

    def _init_using_k_equivalence(self, given_graph, sfa=False):
        """
        Args:
            given_graph (DFA): The DFA states
            sfa (boolean): A boolean for chosing SFA
        Return:
            list, list, list: sm_vector, smi_vector, em_vector initialization vectors
        """
        graph = DFA(self.alphabet)
        graph.init_from_acceptor(given_graph)
        graph.fixminimized(self.alphabet)

        # Access Strings
        self.access_strings_map = self._bfs_path_states(graph, sorted(
            graph.states, key=attrgetter('initial'), reverse=True)[0])

        # Find Q
        set_q = set(self._object_set_to_state_list(graph.states))
        # We will work with states addresses here instead of states stateid for
        # more convenience
        set_f = set(self._object_set_to_state_list(self._get_accepted(graph)))
        # Perform P := {F, Q-F}
        set_nf = set_q.copy() - set_f.copy()
        self.groups = [set_f.copy(), set_nf.copy()]
        self.bookeeping = [(set_f, set_nf, '')]

        done = False
        while not done:
            done = True
            new_groups = []
            for selectgroup in self.groups:
                # _check for each letter if it splits the current group
                for character in self.alphabet:
                    # print 'Testing symbol: ', c
                    target = defaultdict(list)
                    target_states = defaultdict(int)
                    new_g = [set(selectgroup)]
                    for sid in selectgroup:
                        # _check if all transitions using c are going in a state
                        # in the same group. If they are going on a different
                        # group then split
                        deststate = self._delta(graph, graph[sid], character)
                        destgroup = self._get_group_from_state(
                            deststate.stateid)
                        target[destgroup].append(sid)
                        target_states[destgroup] = deststate.stateid
                    if len(target) > 1:

                        inv_target_states = {
                            v: k for k, v in target_states.iteritems()}
                        new_g = [set(selectedstate) for selectedstate in target.values()]
                        done = False
                        # Get all the partitions of destgroups
                        queue = [set([x for x in target_states.values()])]
                        while queue:
                            top = queue.pop(0)
                            (group1, group2, distinguish_string) = self._partition_group(top)
                            ng1 = self._reverse_to_source(
                                target, [inv_target_states[x] for x in group1])
                            ng2 = self._reverse_to_source(
                                target, [inv_target_states[x] for x in group2])
                            dist_string = character + distinguish_string

                            self.bookeeping.append((ng1, ng2, dist_string))

                            if len(group1) > 1:
                                queue.append(group1)
                            if len(group2) > 1:
                                queue.append(group2)
                        break
                new_groups += new_g

            # End of iteration for the k-equivalence
            # Assign new groups and check if any change occured
            self.groups = new_groups

        sm_vector = [
            i for (a, i) in sorted(
                self.access_strings_map.items(),
                key=lambda x: len(x[1]))]
        if not sfa:
            smi_vector = ['{}{}'.format(a, b)
                          for b in self.alphabet for a in sm_vector]
        else:
            smi_vector = self._init_smi(graph, self.access_strings_map)
        em_vector = [distinguish_string for (_, _, distinguish_string) in self.bookeeping]

        return sm_vector, smi_vector, em_vector

    def initialize(self, givengraph, sfa=False):
        """
        Args:
            givengraph (DFA): The DFA states
            sfa (bool): A boolean for chosing SFA
        Return:
            list, list, list: sm_vector, smi_vector, em_vector initialization vectors
        """
        sm_vector, smi_vector, em_vector = self._init_using_k_equivalence(
            givengraph, sfa)
        return sm_vector, smi_vector, em_vector
