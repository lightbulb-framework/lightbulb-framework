"""
This module transforms a pyfst DFA to regular expressions
using the Brzozowski Algebraic Method
"""
import sys
import re
from collections import OrderedDict
from operator import attrgetter

from alphabet import createalphabet
from dfa import DFA
from flex2fst import Flexparser


class Regex:
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

    def _create_map(self):
        """Initialize Brzozowski Algebraic Method"""

        # at state i is represented by the regex self.B[i]
        for state_a in self.mma.states:
            self.A[state_a.stateid] = {}
            # Create a map state to state, with the transition symbols
            for arc in state_a.arcs:
                if arc.nextstate in self.A[state_a.stateid]:
                    self.A[state_a.stateid][arc.nextstate].append(self.mma.isyms.find(arc.ilabel))
                else:
                    self.A[state_a.stateid][arc.nextstate] = [self.mma.isyms.find(arc.ilabel)]
            if state_a.final:
                self.A[state_a.stateid]['string'] = ['']

       # In both self.B and Self.A there are empty spots that we will fill in _brzozowski_algebraic_method_solve

    def _fix_pattern(self):
        for state_a in self.mma.states:
            for target in self.A[state_a.stateid]:
                if len(self.A[state_a.stateid][target]) == 0:
                    self.A[state_a.stateid][target] = ''
                elif len(self.A[state_a.stateid][target]) == 1:
                    self.A[state_a.stateid][target] = self.A[state_a.stateid][target][0]
                elif len(self.A[state_a.stateid][target]) == len(self.alphabet):
                    self.A[state_a.stateid][target] = '.'
                elif len([a for a in self.A[state_a.stateid][target] if len(a) > 1]) == 0 and len(self.A[state_a.stateid][target]) > len(self.alphabet) / 2:
                    self.A[state_a.stateid][target] = '[^' + ''.join(
                        filter(lambda x: x not in self.A[state_a.stateid][target], self.alphabet)) + ']'
                elif len([a for a in self.A[state_a.stateid][target] if len(a) > 1]) == 0 and len(self.A[state_a.stateid][target]) < len(self.alphabet) / 2:
                    self.A[state_a.stateid][target] = '[' + ''.join(self.A[state_a.stateid][target]) + ']'
                elif len([a for a in self.A[state_a.stateid][target] if len(a) > 1]) > 0:
                    self.A[state_a.stateid][target] = '(' + '|'.join(self.A[state_a.stateid][target]) + ')'

    def partitionAlphabet(self, alphabetLen, parsedInput):
        intoInput = []
        notInInput = []
        for c in self.alphabet:
            if c in parsedInput:
                intoInput.append(c)
            else:
                notInInput.append(c)
        if len(intoInput) == alphabetLen:
            return '.'
        if (len(intoInput) < len(notInInput)):
            final = '[' + ''.join(intoInput) + ']'
        else:
            final = '[^' + ''.join(notInInput) + ']'
        return final

    def replaceAlphabet(self, input):
        if "|" not in input:
            return input
        alphabetLen = len(self.alphabet)
        parsedInput = input.split("|")
        if "|||" in input:
            parsedInput.append("|")

        for c in parsedInput:
            if len(c) > 1:
                return input

        final = self.partitionAlphabet(alphabetLen, parsedInput)
        return final

    def cleaner(self, res):
        res = self.replaceAlphabet(res)
        import re
        if '|' in re.sub('\(.*\)', '', res):
            res = '(' + res + ')'
        return res

    def cleanerS(self, res):
        res = self.replaceAlphabet(res)
        import re
        if '|' in re.sub(r'\([^)]*\)', '', res):
            res = '(' + res + ')*'
        return res

    def findWhichSymbolsFromOtherStatesConnectToMe(self, state):
        array = []
        for n in self.A:
            if n != state and state in self.A[n]:
                if self.A[n][state] not in array:
                    array.append(self.A[n][state])
        return array

    def checkIfSameStateNotNeeded(self, state, same):
        array = self.findWhichSymbolsFromOtherStatesConnectToMe(state)
        parts = []
        if len(array) == 0:
            return same
        try:
            if len(self.A[state]['same']) > 3 and self.A[state]['same'][0] == '(' and self.A[state]['same'][
                                                                                            len(self.A[state][
                                                                                                    'same']) - 1:len(
                                                                                                self.A[state][
                                                                                                        'same']) + 1]:
                parts.append(self.A[state]['same'][1:len(self.A[state]['same']) - 2])
            else:
                parts = re.findall(r'\((.+?)\)\*', self.A[state]['same'])

            for n in parts:
                if n[len(n) - 1] != array[0]:
                    return same
            return ''
        except AttributeError:
            return same

    def checkIfBothAreNeeded(self, inputA, inputB):  # based on the fact that ([^b]*|b([^i])*) is equal to  .*
        try:
            input1 = re.search('\(\[\^(.+?)\]\)\*', inputA).group(1)
        except AttributeError:
            input1 = inputA
        try:
            input2FirstChar = re.search('\((.+?)\)\*', inputB).group(1)[0]
        except AttributeError:
            input2FirstChar = inputB[0]

        if len(input1) == 1 and input1 == input2FirstChar:
            return 1
        else:
            return -1

    def replaceAlphabetMixed(self, input1, input2):
        found1 = 0
        found2 = 0
        if "|" not in input1:
            final1 = input1
            if len(input1) > 1:
                found1 = 1
        else:
            parsedInput = input1.split("|")
            for c in parsedInput:
                if len(c) > 1:
                    final1 = input1
                    found1 = 1
                    break

        if "|" not in input2:
            final2 = input2
            if len(input2) > 1:
                found2 = 1
        else:
            parsedInput = input2.split("|")
            for c in parsedInput:
                if len(c) > 1:
                    final2 = input2
                    found2 = 1
                    break

        if found1 == 1 and found2 == 0:
            if (self.checkIfBothAreNeeded(input1, input2) == 1):
                return '(.)*'
            final2 = self.replaceAlphabet(input2)
        if found1 == 0 and found2 == 1:
            if (self.checkIfBothAreNeeded(input1, input2) == 1):
                return '(.)*'
            final1 = self.replaceAlphabet(input1)
        if found1 == 1 and found2 == 1:
            if (self.checkIfBothAreNeeded(input1, input2) == 1):
                return '(.)*'
        if found1 == 0 and found2 == 0:
            final1 = input1
            final2 = input2
        return final1 + "|" + final2

    def getMaxInternalPath(self, inkeys):
        maxkey = 0
        keys = inkeys
        if 'same' in keys:
            keys.remove('same')
        if 'rest' in keys:
            keys.remove('rest')
        if 'string' in keys:
            keys.remove('string')
        if len(keys) > 0:
            maxkey = sorted(keys, reverse=True)[0]
        return maxkey

    def existsPath(self, initial, finalstate, visited):
        for i in self.A:
            if finalstate in self.A[i] and i not in visited:
                if i == initial:
                    return 1, self.A[i][finalstate], finalstate
                else:
                    visited.append(i)
                    res, key, transfer_state = self.existsPath( initial, i, visited)
                    if res == 1:
                        return 1, key, finalstate
                    else:
                        continue
            else:
                continue
        return 0, 0, 0
    def fixBrzozowskiBackwardLoopRemoval(self):

        # Remove targets that point to start
        for i in self.A:
            if i != 0:
                for target in self.A[i].keys():
                    if target == 0:
                        self.A[i].pop(target)

        for i in self.A:
            poplist = []
            for target in self.A[i]:
                if target < i:
                    exists, transfer_value, transfer_state = self.existsPath(target, i, [])

                    if exists and (transfer_value == self.A[i][target] or (target in self.A[target] and (self.A[target][target] == self.A[i][target] or len(
                                set(self.A[i][target]) - set(self.A[target][target])) == 0))):
                        poplist.append(target)
            for k in poplist:
                self.A[i].pop(k)


    def _Lexical(self):
        found = 0
        start = 0
        # First Try to Optimize the Strings by doing the possible replacements of special cases to string. e.c change a loop with character e to (e)*
        for state_a in self.A.keys():
            # Loopholes
            if state_a in self.A[state_a]:
                same = ''
                if 'same' in self.A[state_a]:
                    same = '|' + self.A[state_a]['same']
                    self.A[state_a]['same'] = '(' + ''.join(self.replaceAlphabet(self.A[state_a][state_a])) + ')*' + same
                del(self.A[state_a][state_a])
            # Final State
            if len(self.A[state_a].keys()) == 1 and 'string' in self.A[state_a].keys():
                for state_b in self.A:
                    if state_b != state_a  and state_b in self.A:
                        if state_a in self.A[state_b]:
                            if 'rest' in self.A[state_b] and self.A[state_b]['rest'] != '' and  self.A[state_b]['rest'] == self.cleaner(self.A[state_a]['string']):


                                if 'string' not in self.A[state_b]:
                                    self.A[state_b]['string'] = "(" + self.A[state_b][state_a] + ")?"+self.A[state_b]['rest']
                                else:
                                    self.A[state_b]['string'] = "("+ self.A[state_b]['string']+"|(" + self.A[state_b][state_a] + ")?"+self.A[state_b]['rest']+")"
                                del (self.A[state_b][state_a])
                                del (self.A[state_b]['rest'])
                                found = 1
                            else:
                                newinput = ''.join(self.A[state_b][state_a]) + self.cleaner(self.A[state_a]['string'])
                                if 'rest' in self.A[state_b] and self.A[state_b]['rest'] != '':
                                    newinput = '(' + newinput + '|' + self.A[state_b]['rest'] + ')'

                                self.A[state_b]['rest'] = newinput
                                del (self.A[state_b][state_a])
                                found = 1
                if state_a != start:
                    del (self.A[state_a])
            if state_a != start and state_a in self.A and len(self.A[state_a].keys()) == 1 and 'same' in self.A[state_a].keys():
                del (self.A[state_a])
                for state_b in self.A:
                    if state_b in self.A and state_a in self.A[state_b]:
                        del (self.A[state_b][state_a])
                        found = 1
            # Clean Loophole
            if state_a in self.A and len(self.A[state_a].keys()) == 1 and 'same' in self.A[state_a].keys():
                del (self.A[state_a])
                found = 1
            # Final State
            if state_a in self.A and len(self.A[state_a].keys()) == 1 and 'rest' in self.A[state_a]:
                self.A[state_a]['string'] = self.A[state_a]['rest']
                del (self.A[state_a]['rest'])
                found = 1
            # Final State with alternative path
            if state_a in self.A and len(self.A[state_a].keys()) == 2 and 'string' in self.A[state_a] and 'rest' in \
                    self.A[state_a]:
                if self.A[state_a]['rest'] != '':
                    self.A[state_a]['string'] = self.cleaner(self.A[state_a]['string']) + '(' + self.replaceAlphabet(
                        self.A[state_a]['rest']) + ')?'
                del (self.A[state_a]['rest'])
                found = 1
            # State with alternative path and self loop
            if state_a in self.A and len(self.A[state_a].keys()) == 2 and 'same' in self.A[state_a] and 'rest' in \
                    self.A[state_a]:
                self.A[state_a]['rest'] = self.checkIfSameStateNotNeeded( state_a, self.cleanerS(self.A[state_a][
                    'same'])) + self.cleaner(self.A[state_a]['rest'])
                del (self.A[state_a]['same'])
                found = 1
            # Final State with self loop
            if state_a in self.A and len(self.A[state_a].keys()) == 2 and 'string' in self.A[state_a] and 'same' in \
                    self.A[state_a]:
                self.A[state_a]['string'] = self.checkIfSameStateNotNeeded( state_a, self.cleanerS(self.A[state_a]['same'])) + self.cleaner(self.A[state_a]['string'])
                del (self.A[state_a]['same'])
                found = 1
            # Final State with alternative path and self loop
            if state_a in self.A and len(self.A[state_a].keys()) == 3 and 'string' in self.A[state_a] and 'rest' in \
                    self.A[state_a] and 'same' in self.A[state_a]:
                if self.A[state_a]['rest'] != '':
                    add = '(' + self.A[state_a]['rest'] + ')?'
                self.A[state_a]['string'] = self.checkIfSameStateNotNeeded(state_a, self.cleanerS(self.A[state_a]['same'])) + self.cleaner(self.A[state_a]['string']) + add
                del (self.A[state_a]['rest'])
                del (self.A[state_a]['same'])
                found = 1
            # No path State
            if state_a != start and state_a in self.A and len(self.A[state_a].keys()) == 0:
                del (self.A[state_a])
                for state_b in self.A:
                    if state_b in self.A and state_a in self.A[state_b]:
                        del (self.A[state_b][state_a])

        return found

    def fixBrzozowskiAdvanced(self, found):
        start = 0
        for state_a in self.A:
            maxkey = self.getMaxInternalPath(self.A[state_a].keys())
            if state_a != start and state_a in self.A and maxkey < state_a and (
                (len(self.A[state_a].keys()) > 1) or (len(self.A[state_a].keys()) == 1 and 'same' not in self.A[state_a])):
                same = ''
                if 'same' in self.A[state_a]:
                    same = self.checkIfSameStateNotNeeded( state_a, self.cleanerS(self.A[state_a]['same']))
                # del(self.A[i]['same'])
                for state_b in [x.stateid for x in self._bfs_sort(sorted(self.mma.states,key=attrgetter('initial'),reverse=True)[0])]:
                    if state_b != state_a and state_b in self.A:
                        if state_a in self.A[state_b]:
                            temp = self.cleaner(self.A[state_b][state_a])
                            del (self.A[state_b][state_a])
                            for newTarget in self.A[state_a]:
                                if newTarget != 'same':
                                    transValue = same + self.cleaner( self.A[state_a][newTarget])
                                    found = 1
                                    add = temp + transValue
                                    if newTarget == state_b:
                                        newTarget = 'same'
                                        add = '(' + self.replaceAlphabet(add) + ')*'
                                    if ((newTarget not in self.A[state_b]) or (self.A[state_b][newTarget] == '')):
                                        self.A[state_b][newTarget] = add
                                    else:
                                        self.A[state_b][newTarget] = self.replaceAlphabetMixed(self.A[state_b][newTarget], add)
                                    found = 1

                            if found == 1:
                                break

        return found


    def _solve(self):
        self._create_map()
        self._fix_pattern()
        self.fixBrzozowskiBackwardLoopRemoval()  # Remove backward paths because of kleene star

        while 1:
            found = self._Lexical()
            if found == 0:
                found = self.fixBrzozowskiAdvanced(found)
            if found == 0:
                break
        if 'string' in self.A[0]:
            return ''.join(self.A[0]['string'].splitlines())

    def get_regex(self):
        """Generate regular expressions from DFA automaton"""

        return self._solve()

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
    print 'OK'
    print 'Perform Brzozowski on minimal automaton:',
    brzozowski_a = Regex(mma)
    mma_regex = brzozowski_a.get_regex()
    print mma_regex

if __name__ == '__main__':
    main()
