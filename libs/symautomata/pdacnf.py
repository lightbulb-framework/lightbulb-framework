"""This module generates a CNF grammar from a PDA object"""
from sys import argv

from alphabet import createalphabet
from cfggenerator import CFGGenerator, CNFGenerator
from cfgpda import CfgPDA
from pda import PDAState

class IntersectionHandling():
    """
    After the intersection (product operation) there would be final
    transitions to non accepted states (according to the DFA
    accepted states). These transitions should be removed before
    generating the CFG
    """

    def __init__(self):
        pass

    def get(self, statediag, dfaaccepted):
        """
        # - Remove all the POP (type - 2) transitions to state 0,non DFA accepted
        # for symbol @closing
        # - Generate the accepted transitions
        - Replace DFA accepted States with a push - pop symbol and two extra states
        Args:
            statediag (list): The states of the PDA
            dfaaccepted (list):The list of DFA accepted states
        Returns:
            list: A cleaned, smaller list of DFA states
        """

        newstatediag = {}

        newstate = PDAState()
        newstate.id = 'AI,I'  # BECAREFUL WHEN SIMPLIFYING...
        newstate.type = 1
        newstate.sym = '@wrapping'
        transitions = {}
        transitions[(0, 0)] = [0]
        newstate.trans = transitions
        i = 0
        newstatediag[i] = newstate
        # print 'accepted:'
        # print dfaaccepted
        for stateid in statediag:
            state = statediag[stateid]
            # print state.id
            if state.type == 2:
                for state2id in dfaaccepted:
                    # print state.id[1]
                    if state.id[1] == state2id:
                        # print 'adding...'
                        state.trans['AI,I'] = ['@wrapping']
                        # print state.trans
                        break
            i = i + 1
            newstatediag[i] = state
        return newstatediag


class ReducePDA():
    """Use BFS to search for unreachable states and remove them"""
    def __init__(self):
        pass

    def bfs(self, graph, start):
        """
        Performs BFS operation for eliminating useless loop transitions
        Args:
            graph (PDA): the PDA object
            start (PDA state): The PDA initial state
        Returns:
            list: A cleaned, smaller list of DFA states
        """
        newstatediag = {}

        # maintain a queue of paths
        queue = []
        visited = []
        # push the first path into the queue
        queue.append(start)
        while queue:
            # get the first path from the queue
            state = queue.pop(0)
            # get the last node from the path
            # visited
            visited.append(state.id)
            # enumerate all adjacent nodes, construct a new path and push it
            # into the queue
            for key in state.trans:
                if state.trans[key] != []:
                    if key not in visited:
                        for nextstate in graph:
                            if graph[nextstate].id == key:
                                queue.append(graph[nextstate])
                                break
        i = 0
        for state in graph:
            if graph[state].id in visited:
                newstatediag[i] = graph[state]
                i = i + 1

        return newstatediag

    def get(self, statediag):
        """
        Args:
            statediag (list): The states of the PDA
        Returns:
            list: A reduced list of states using BFS
        """
        if len(statediag) < 1:
            print 'PDA is empty and can not be reduced'
            return statediag
        newstatediag = self.bfs(statediag, statediag[0])
        return newstatediag


class SimplifyStateIDs():
    """
    Transform state IDs to a more simple form (sequencial numbers).
    Should be used after product operation (intersection)
    """

    def __init__(self):
        pass

    def get(self, statediag, accepted=None):
        """
        Replaces complex state IDs as generated from the product operation,
        into simple sequencial numbers. A dictionaty is maintained in order
        to map the existed IDs.
        Args:
            statediag (list): The states of the PDA
            accepted (list): the list of DFA accepted states
        Returns:
            list:
        """
        count = 0
        statesmap = {}
        newstatediag = {}
        for state in statediag:

            # Simplify state IDs
            if statediag[state].id not in statesmap:
                statesmap[statediag[state].id] = count
                mapped = count
                count = count + 1
            else:
                mapped = statesmap[statediag[state].id]

            # Simplify transitions IDs

            transitions = {}
            for nextstate in statediag[state].trans:
                if nextstate not in statesmap:
                    statesmap[nextstate] = count
                    transmapped = count
                    count = count + 1
                else:
                    transmapped = statesmap[nextstate]
                transitions[transmapped] = statediag[state].trans[nextstate]
            newstate = PDAState()
            newstate.id = mapped
            newstate.type = statediag[state].type
            newstate.sym = statediag[state].sym
            newstate.trans = transitions
            newstatediag[mapped] = newstate
        newaccepted = None
        if accepted is not None:
            newaccepted = []
            for accepted_state in accepted :
                if (0, accepted_state) in statesmap:
                    newaccepted.append(statesmap[(0, accepted_state)])
        return newstatediag, count, newaccepted


class ReadReplace():
    """
    Removes all READ (type - 3) states and replaces them with PUSH (type - 1) and POP (type - 2).
    Should be used before PDA to CFG operation.
    """

    statediag = []
    quickresponse = {}
    quickresponse_types = {}
    toadd = []
    biggestid = 0

    def __init__(self, statediag=[], thebiggestid=None):
        """
        Find the biggest State ID
        Args:
            statediag (list): The states of the PDA
            thebiggestid (int): The binggest state identifier
        Returns:
            None
        """
        self.statediag = []
        self.quickresponse = {}
        self.quickresponse_types = {}
        self.toadd = []
        self.biggestid = 0

        if thebiggestid is None:
            for state in statediag:
                if statediag[state].id > self.biggestid:
                    self.biggestid = statediag[state].id
        else:
            self.biggestid = thebiggestid
        self.statediag = statediag

    def nextstate(self):
        """
        Always return the biggest state ID + 1
        """
        self.biggestid = self.biggestid + 1
        return self.biggestid

    def _generate_state(self, trans):
        """
        Creates a new POP state (type - 2) with the same transitions.
        The POPed symbol is the unique number of the state.
        Args:
            trans (dict): Transition dictionary
        Returns:
            Int: The state identifier
        """
        state = PDAState()
        state.id = self.nextstate()
        state.type = 2
        state.sym = state.id
        state.trans = trans.copy()
        self.toadd.append(state)
        return state.id

    def replace_read(self):
        """
        Replaces all READ (type - 3) states to a PUSH (type - 1) and a POP (type - 2).
        The actual state is replaced with the PUSH, and a new POP is created.
        """
        for statenum in self.statediag:
            state = self.statediag[statenum]
            if state.type == 3:  # READ state
                state.type = 1
                destination_and_symbol = self._generate_state(state.trans)
                state.sym = destination_and_symbol
                state.trans = {}
                state.trans[destination_and_symbol] = [0]
        statenumber_identifier = len(self.statediag) + 1
        for state in self.toadd:
            self.statediag[statenumber_identifier] = state
            statenumber_identifier = statenumber_identifier + 1
        return self.statediag


class PdaCnf():
    """This class manages PDA to CNF generation"""
    rules = []
    statediag = []
    accepted = []

    def insert_start_to_accepting(self):
        """
        Insert the start rule S -> A0,0
            or alphabet -> AI,I (IF intersected, the DFA Accepted states
            will be eliminated by adding a wrapping state with push pop symbol)
        """
        self.rules.append('S: A0,0')

    def insert_self_to_empty_and_insert_all_intemediate(self, optimized):
        """
        For each state qi of the PDA, we add the rule Aii -> e
        For each triplet of states qi, qj and qk, we add the rule Aij -> Aik Akj.
        Args:
            optimized (bool): Enable or Disable optimization - Do not produce O(n^3)
        """
        for state_a in self.statediag:
            self.rules.append('A' +repr(state_a.id) +',' + repr(state_a.id) + ': @empty_set')

            # If CFG is not requested, avoid the following O(n^3) rule.
            # It can be solved and a string can be generated faster with BFS of DFS

            if optimized == 0:
                for state_b in self.statediag:
                    if state_b.id != state_a.id:
                        for state_c in self.statediag:
                            if state_c.id != state_a.id \
                                    and state_b.id != state_c.id:
                                self.rules.append('A' + repr(state_a.id)
                                                  + ',' + repr(state_c.id)
                                                  + ': A' + repr(state_a.id)
                                                  + ',' + repr(state_b.id)
                                                  + ' A' + repr(state_b.id)
                                                  + ',' + repr(state_c.id)
                                                  + '')

    def insert_symbol_pushpop(self):
        """
        For each stack symbol t E G, we look for a pair of states, qi and qj,
        such that the PDA in state qi can read some input a E S and push t
        on the stack and in state state qj can read some input b E S and pop t
        off the stack. In that case, we add the rule Aik -> a Alj b
        where (ql,t) E d(qi,a,e) and (qk,e) E d(qj,b,t).
        """

        for state_a in self.statediag:
            if state_a.type == 1:
                found = 0
                for state_b in self.statediag:
                    if state_b.type == 2 and state_b.sym == state_a.sym:
                        found = 1
                        for j in state_a.trans:
                            if state_a.trans[j] == [0]:
                                read_a = ''
                            else:
                                new = []
                                for selected_transition in state_a.trans[j]:
                                    if selected_transition == ' ':
                                        new.append('&')
                                    else:
                                        new.append(selected_transition)

                                read_a = " | ".join(new)
                            for i in state_b.trans:
                                if state_b.trans[i] == [0]:
                                    read_b = ''
                                else:
                                    new = []
                                    for selected_transition in state_b.trans[i]:
                                        if selected_transition == ' ':
                                            new.append('&')
                                        else:
                                            new.append(selected_transition)
                                    read_b = " | ".join(new)
                                self.rules.append(
                                    'A' + repr(state_a.id)
                                    + ',' + repr(i)
                                    + ':' + read_a
                                    + ' A' + repr(j)
                                    + ',' + repr(state_b.id)
                                    + ' ' + read_b)
                if found == 0:

                    # A special case is required for State 2, where the POPed symbols
                    # are part of the transitions array and not defined for "sym" variable.

                    for state_b in self.statediag:
                        if state_b.type == 2 and state_b.sym == 0:
                            for i in state_b.trans:
                                if state_a.sym in state_b.trans[i]:
                                    for j in state_a.trans:
                                        if state_a.trans[j] == [0]:
                                            read_a = ''
                                        else:
                                            read_a = " | ".join(
                                                state_a.trans[j])
                                        self.rules.append(
                                            'A' + repr(state_a.id)
                                            + ',' + repr(i)
                                            + ':' + read_a
                                            + ' A' + repr(j)
                                            + ',' + repr(state_b.id))
                                        # print
                                        # 'A'+`state_a.id`+','+`i`+':'+read_a+'
                                        # A'+`j`+','+`state_b.id`
                                        found = 1
                if found == 0:
                    print "ERROR: symbol " + repr(state_a.sym) \
                          + ". It was not found anywhere in the graph."

    def get_rules(self, optimized):
        """
        Args:
            optimized (bool): Enable or Disable optimization - Do not produce O(n^3)
        Return:
            list: The CFG rules
        """
        self.insert_start_to_accepting()
        # If CFG is not requested, avoid the following O(n^3) rule.
        # It can be solved and a string can be generated faster with BFS of DFS

        if optimized == 0:
            self.insert_self_to_empty_and_insert_all_intemediate(optimized)
        self.insert_symbol_pushpop()
        return self.rules

    def __init__(self, states, dfaaccepted=[]):
        self.rules = []
        self.statediag = []
        self.accepted = []
        self.accepted = dfaaccepted
        for key in states:
            self.statediag.append(states[key])


def _read_file(fname):
    """
    Args:
        fname (str): Name of the grammar file to be parsed
    Return:
        list: The grammar rules
    """
    with open(fname) as input_file:
        re_grammar = [x.strip('\n') for x in input_file.readlines()]
    return re_grammar


def main():
    """
    Function for PDA to CNF Operation
    :type argv: list
    :param argv: Parameters
    """
    if len(argv) < 3:
        print 'Usage for getting CFG: %s CFG_fileA CFG ' % argv[0]
        print 'Usage for getting STR: %s CFG_fileA STR ' \
              'Optimize[0 or 1] splitstring[0 or 1] ' % argv[0]
        print ''
        print 'For example: python pdacnf.py grammar.y STR 1 0'
        print '             python pdacnf.py grammar.y STR 1 1'
        print '             python pdacnf.py grammar.y CFG'
        return

    alphabet = createalphabet()

    mode = argv[2]

    optimized = 0
    splitstring = 0
    if mode == 'STR':
        optimized = int(argv[3])
        splitstring = int(argv[4])

    cfgtopda = CfgPDA(alphabet)
    print '* Parsing Grammar:',
    mma = cfgtopda.yyparse(argv[1])
    print 'OK'
    print ' - Total PDA states are ' + repr(len(mma.s))

    print '* Simplify State IDs:',
    simple_a = SimplifyStateIDs()
    mma.s, biggestid, newaccepted = simple_a.get(mma.s)
    if newaccepted:
        print 'OK'
    else:
        print 'OK'

    print '* Eliminate READ states:',
    replace = ReadReplace(mma.s, biggestid)
    mma.s = replace.replace_read()
    print 'OK'
    print ' - Total PDA states now are ' + repr(len(mma.s))
    maxstate = replace.nextstate() - 1

    print '* Reduce PDA:',
    simple_b = ReducePDA()
    mma.s = simple_b.get(mma.s)
    print 'OK'
    print ' - Total PDA states now are ' + repr(len(mma.s))

    print '* PDA to CFG transformation:',
    cnfgenerator = PdaCnf(mma.s)
    grammar = cnfgenerator.get_rules(optimized)
    print 'OK'
    print ' - Total CFG rules generated: ' + repr(len(grammar))

    if mode == 'STR':
        gen = CFGGenerator(CNFGenerator(grammar),
                           optimized=optimized,
                           splitstring=splitstring,
                           maxstate=maxstate)
        print gen.generate()
    else:
        print grammar


    # For example, for given cfg:
    #
    #     S: main
    #     main: 1 mainnew 1
    #     mainnew:  u
    #     mainnew:  main
    #
    # the generated grammar (optimized) would be:
    #
    # ['S: A0,0', 'A0,0: A1,2', 'A1,3: A2,2', 'A3,9: A11,2',
    # 'A4,8: A12,2', 'A5,2: A18,18 u', 'A6,7: A13,2',
    # 'A7,10: A14,2', 'A8,10: A15,2', 'A9,10: A16,2',
    # 'A10,2: A19,19 1', 'A11,10: A2,2', 'A12,10: A2,2',
    #  'A13,10: A2,2', 'A14,5: A2,2', 'A14,6: A2,2',
    # 'A15,5: A2,2', 'A15,6: A2,2', 'A16,5: A2,2', 'A16,6: A2,2']
    #
    # and can be solved as following:
    #
    #     S: A0,0
    #     S: A1,2
    #     S: (A1,3 A3,2)
    #     S: A2,2 (A3,9 A9,2)
    #     S: A11,2 (A9,10 A10,2)
    #     S: (A11,10 A10,2) (A16,2 A19,19 1)
    #     S: (A2,2  A19,19 1) ((A16,5 A5,2) 1)
    #     S:  1 (A2,2 (A18,18 u)) 1
    #     S: 1u1



if __name__ == '__main__':
    main()
