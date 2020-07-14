"""
This module performs Diff operation
between a PDA and a DFA
"""
import time
from sys import argv

import datetime
import dateutil.relativedelta
from alphabet import createalphabet
from cfggenerator import CFGGenerator, CNFGenerator
from cfgpda import CfgPDA
from flex2fst import Flexparser
from pda import PDA, PDAState
from pdacnf import PdaCnf, IntersectionHandling, SimplifyStateIDs, ReadReplace, ReducePDA
from pdastring import PdaString
from dfa import TropicalWeight

class PdaDiff():
    """Performs Diff operation between a PDA and a DFA"""

    def __init__(self, input_pda_a, input_dfa_b, alphabet):
        """
        Args:
            input_pda_a (PDA): The input PDA
            input_dfa_b (DFA): The input pyfst DFA
        Returns:
            None
        """
        self.mma = input_pda_a
        self.mmb = None
        if input_dfa_b:
            self.mmb = input_dfa_b.copy()
        self.mmc = None
        self.alphabet = alphabet

    def _delta(self, graph, cur_state, char):
        """
        Args:
            graph (Fst Acceptor): The DFA
            cur_state (Fst State): The current State
            char (Char): The input character
        Returns:
            (Fst State): The destination state
        """
        for arc in cur_state.arcs:
            if graph.isyms.find(arc.ilabel) == char:
                return graph[arc.nextstate]
        return None

    def _break_terms(self):
        counter = len(self.mma.s)
        for state in self.mma.s.keys():
            if self.mma.s[state].type == 3:
                for transition in self.mma.s[state].trans.keys():
                    for transition in self.mma.s[state].trans.keys():
                        for record in self.mma.s[state].trans[transition]:
                            if len(record) > 1:
                                    value = record
                                    i = self.mma.s[state].trans[transition].index(record)
                                    del self.mma.s[state].trans[transition][i]
                                    if len(self.mma.s[state].trans[transition]) == 0:
                                        del self.mma.s[state].trans[transition]
                                    tempstate = PDAState()
                                    tempstate.id = counter
                                    tempstate.sym = 0
                                    tempstate.type = 3
                                    tempstate.trans = {}
                                    tempstate.trans[transition] = [value[-1]]
                                    self.mma.s[counter] = tempstate
                                    counter = counter + 1
                                    for character in reversed(value[1:-1]):
                                        tempstate = PDAState()
                                        tempstate.id = counter
                                        tempstate.sym = 0
                                        tempstate.type = 3
                                        tempstate.trans = {}
                                        tempstate.trans[counter-1] = [character]
                                        self.mma.s[counter] = tempstate
                                        counter = counter + 1

                                    self.mma.s[state].trans[counter-1] = [value[0]]
        self.mma.n = counter-1


    def _intesect(self):
        """The intesection of a PDA and a DFA"""
        p1automaton = self.mma
        p2automaton = self.mmb
        p3automaton = PDA(self.alphabet)
        self._break_terms()
        p1counter = 0
        p3counter = 0
        p2states = list(p2automaton.states)
        print 'PDA States: ' + repr(p1automaton.n)
        print 'DFA States: ' + repr(len(list(p2states)))
        ignorechars = p1automaton.nonterminals+ [0] + ['@closing']
        del(ignorechars[ignorechars.index('S')])
        while p1counter < p1automaton.n + 1:
            p1state = p1automaton.s[p1counter]
            p2counter = 0
            while p2counter < len(list(p2states)):
                p2state = p2states[p2counter]
                tempstate = PDAState()
                tempstate.id = (p1state.id, p2state.stateid)
                tempstate.sym = p1state.sym
                tempstate.type = p1state.type
                tempstate.trans = {}
                found = 0
                for char in self.alphabet:
                    if char in ignorechars:
                        continue
                    # DFA has single destination from a state
                    p2dest = self._delta(p2automaton, p2state, char)
                    # PDA may have multiple destinations from a state
                    # print p1state.trans
                    if p2dest is not None:
                        for potential in p1state.trans:
                            if char in p1state.trans[potential]:
                                found = 1
                                p1dest = potential
                                if (p1dest,
                                        p2dest.stateid) not in tempstate.trans:
                                    tempstate.trans[
                                        (p1dest, p2dest.stateid)] = []
                                    # print 'Appending A Transition to
                                    # ('+`p1dest`+','+`p2dest.stateid`+') for
                                    # input '+`char`
                                tempstate.trans[
                                    (p1dest, p2dest.stateid)].append(char)

                                # THEN THE NONTERMINALS + 0 3 transitions
                                # print p1state.trans
                                #               print p1automaton.nonterminals
                if found == 0 and  p1state.type == 3 and len(p1state.trans) >0:
                    assert 1==1,'Check Failed: A READ state with transitions' \
                                ' did not participate in the cross product'
                if p2dest is not None:
                    for nonterm in p1automaton.nonterminals + \
                            [0] + ['@closing']:
                        for potential in p1state.trans:
                            if nonterm in p1state.trans[potential]:
                                p1dest = potential
                                if (p1dest,
                                        p2state.stateid) not in tempstate.trans:
                                    tempstate.trans[
                                        (p1dest, p2state.stateid)] = []
                                # print 'Appending B Transition to
                                # ('+`p1dest`+','+`p2state.stateid`+') for
                                # input '+`nonterm`
                                tempstate.trans[
                                    (p1dest, p2state.stateid)].append(nonterm)
                p3automaton.s[p3counter] = tempstate
                p3counter = p3counter + 1
                p2counter = p2counter + 1
            p1counter = p1counter + 1
        # print 'Total States Appended '+`len(p3automaton.input_string)`
        p3automaton.n = p3counter - 1

        p3automaton.accepted = []
        for state in p2automaton.states:
            if state.final != TropicalWeight(float('inf')):
                p3automaton.accepted.append(state.stateid)
        return p3automaton

    def diff(self):
        """The Difference between a PDA and a DFA"""
        self.mmb.complement(self.alphabet)
        self.mmb.minimize()
        print 'start intersection'
        self.mmc = self._intesect()
        print 'end intersection'
        return self.mmc

    def get_string(self):
        """
        Returns a string from the Diff resutl.
        Depending on the method, either the string will
        be generated directly from the PDA using the state
        removal method, or the PDA will be first translated to
        a CFG and then a string will be generated from the CFG
        Args:
             None
        Returns:
            A string from the Diff
        """
        return_string = None
        if not self.mmc:
            return ""
        method = 'PDASTRING'
        if method == 'PDASTRING':
            stringgen = PdaString()
            print '* Reduce PDA using DFA BFS (remove unreachable states):'
            newpda = self.mmc.s
            handle = IntersectionHandling()
            newpda = handle.get(newpda, self.mmc.accepted)
            reduce_b = ReducePDA()
            newpda = reduce_b.get(newpda)
            #simply = SimplifyStateIDs()
            #newpda, biggestid, newaccepted = simply.get(
            #    newpda, self.mmc.accepted)
            print "- Total PDA states after reduction are " + repr(len(newpda))
            return_string = stringgen.init(newpda, self.mmc.accepted)
            if return_string is not None:
                return_string = return_string[0]
        elif method == 'PDACFGSTRING':

            optimized = 1
            dt1 = datetime.datetime.fromtimestamp(time.time())
            print '* Initiating PDA simplification'
            print ' - Total PDA states are ' + repr(len(self.mmc.s))
            handle = IntersectionHandling()
            newpda = handle.get(self.mmc.s, self.mmc.accepted)
            newpda = self.mmc.s
            simply = SimplifyStateIDs()
            newpda, biggestid, newaccepted = simply.get(
                newpda, self.mmc.accepted)
            print ' - Total PDA states after id clearence are ' + repr(len(newpda))
            replace = ReadReplace(newpda, biggestid)
            newpda = replace.replace_read()
            print ' - Total PDA states after read elimination are ' + repr(len(newpda))
            maxstate = replace.nextstate() - 1
            print '* Reduce PDA using DFA BFS (remove unreachable states):'
            reduce_b = ReducePDA()
            newpda = reduce_b.get(newpda)
            print "- Total PDA states after reduction are " + repr(len(newpda))

            dt2 = datetime.datetime.fromtimestamp(time.time())
            rdelta = dateutil.relativedelta.relativedelta(dt2, dt1)
            print "* PDA was simplyfied in %d days, %d hours, %d minutes and %d seconds" % (
                rdelta.days, rdelta.hours, rdelta.minutes, rdelta.seconds)
            dt1 = datetime.datetime.fromtimestamp(time.time())
            print '* Initiating CNF from PDA generation'
            cnfgenerator = PdaCnf(newpda, newaccepted)
            dt2 = datetime.datetime.fromtimestamp(time.time())
            rdelta = dateutil.relativedelta.relativedelta(dt2, dt1)
            print "* CNF was generated in %d days, %d hours, %d minutes and %d seconds" % (
                rdelta.days, rdelta.hours, rdelta.minutes, rdelta.seconds)
            dt1 = datetime.datetime.fromtimestamp(time.time())
            print '* Initiating string from CFG generation'
            grammar = cnfgenerator.get_rules(optimized)
            print ' - Total grammar rules are ' + repr(len(grammar))
            gen = CFGGenerator(CNFGenerator(grammar),
                               optimized=optimized,
                               splitstring=0,
                               maxstate=maxstate)
            return_string = gen.generate()
            dt2 = datetime.datetime.fromtimestamp(time.time())
            rdelta = dateutil.relativedelta.relativedelta(dt2, dt1)
            print "* A string was generated in %d days, %d hours, %d minutes and %d seconds" % (
                rdelta.days, rdelta.hours, rdelta.minutes, rdelta.seconds)

            print return_string
        else:
            return_string = None
        return return_string


def main():
    """
    Testing function for PDA - DFA Diff Operation
    """
    if len(argv) < 2:
        print 'Usage: '
        print '         Get A String              %s CFG_fileA FST_fileB' % argv[0]
        return

    alphabet = createalphabet()

    cfgtopda = CfgPDA(alphabet)
    print '* Parsing Grammar:',
    mma = cfgtopda.yyparse(argv[1])
    print 'OK'

    flex_a = Flexparser(alphabet)
    print '* Parsing Regex:',
    mmb = flex_a.yyparse(argv[2])
    print mmb
    print 'OK'
    print '* Minimize Automaton:',
    mmb.minimize()
    print 'OK'
    print mmb
    print '* Diff:',
    ops = PdaDiff(mma, mmb, alphabet)
    mmc = ops.diff()
    print 'OK'
    print '* Get String:',
    print ops.get_string()


if __name__ == '__main__':
    main()
