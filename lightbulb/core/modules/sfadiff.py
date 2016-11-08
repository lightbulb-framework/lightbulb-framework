"""This module contains the SFADiff algorithm"""
from sfalearn.angluin_sfa import SFALearner as _SFALearner
from symautomata.cfgpda import CfgPDA as _CfgPDA
from symautomata.dfa import DFA as _DFA
from symautomata.flex2fst import Flexparser as _Flexparser
from lightbulb.core.utils.common import accept_bool, findlibrary
from lightbulb.core.utils.rcadiff import rca_diff
from lightbulb.core.base import createalphabet

META = {
    'author': 'George Argyros, Ioannis Stais',
    'name': 'SFADiff',
    'description': 'A black-box differential testing framework based '
                   'on Symbolic Finite Automata (SFA) learning.',
    'type': 'CORE',
    'options': [
        ('ALPHABET', None, True, 'File containing the alphabet'),
        ('SEED_FILE', None, True, 'File containting regular expressions/grammar'),
        ('SEED_FILE_TYPE', "FLEX", True, 'File type (e.g FLEX, GRAMMAR, FST)'),
        ('TESTS_FILE', None, True, 'File containting regular expressions/grammar'),
        ('TESTS_FILE_TYPE', "FLEX", True, 'File type (e.g FLEX, GRAMMAR, FST)'),
        ('DFA1_MINUS_DFA2', False, False, 'Preload the input filter'),
        ('HANDLER', None, True, 'Handler for membership query function'),
   ],
    'comments': ['SFADiff can automatically find differences between '
                 'a set of programs with comparable functionality. '
                 'Unlike existing differential testing techniques, '
                 'instead of searching for each difference individually, '
                 'SFADiff infers SFA models of the target programs '
                 'using black-box queries and systematically enumerates'
                 'the differences between the inferred SFA models']
}

class SFADiff(_SFALearner):
    """SFADiff algorithm module"""

    def __init__(self, configuration, shared_memory, cross):
        self.setup(configuration)
        if not self.alphabet or isinstance(self.alphabet, str):
            self.alphabet = createalphabet(self.alphabet)
        super(SFADiff, self).__init__(self.alphabet)
        self.membership_queries = 0
        self.cache_membership_queries = 0
        self.equivalence_queries = 0
        self.cache_equivalence_queries = 0
        self.cache_equivalence = []
        self.cache_membership = {}
        self.ids_membership_queries = 0
        self.ids_cache_membership_queries = 0
        self.ids_equivalence_queries = 0
        self.ids_cache_equivalence_queries = 0
        self.ids_states = 0
        self.browserstates = 0
        self.cross_check_times = 0
        self.equivalence_queries_cached_membership = 0
        self.ids_equivalence_queries_cached_membership = 0
        self.num_diff = 2
        self.shared_memory = shared_memory
        self.cross = cross
        self.dfa1_minus_dfa2 = accept_bool(self.dfa1_minus_dfa2)
        self.mma = None
        self.mmac = None
        self.pda = None
        self.bypass = None

        if self.seed_file is not None and self.seed_file_type is not None:
            if self.seed_file_type == "FLEX":
                flex_object_m = _Flexparser(self.alphabet)
                self.mma = flex_object_m.yyparse(findlibrary(self.seed_file))
                self.mma.minimize()
            elif self.seed_file_type == "GRAMMAR":
                cfgtopda = _CfgPDA(self.alphabet)
                self.mma = cfgtopda.yyparse(findlibrary(self.seed_file), 1)
            elif self.seed_file_type == "FST":
                self.mma = _DFA(self.alphabet)
                self.mma.load(findlibrary(self.seed_file))
                self.mma.minimize()

        if self.tests_file is not None and self.tests_file_type is not None:
            if self.tests_file_type == "FLEX":
                flex_object_m = _Flexparser(self.alphabet)
                self.mmac = flex_object_m.yyparse(findlibrary(self.tests_file))
                self.mmac.minimize()
            elif self.tests_file_type == "GRAMMAR":
                cfgtopda = _CfgPDA(self.alphabet)
                self.mmac = cfgtopda.yyparse(findlibrary(self.tests_file), 1)
            elif self.tests_file_type == "FST":
                self.mmac = _DFA(self.alphabet)
                self.mmac.load(findlibrary(self.tests_file))
                self.mmac.minimize()

    def setup(self, configuration):
        self.alphabet = configuration['ALPHABET']
        self.seed_file = configuration['SEED_FILE']
        self.seed_file_type = configuration['SEED_FILE_TYPE']
        self.tests_file = configuration['TESTS_FILE']
        self.tests_file_type = configuration['TESTS_FILE_TYPE']
        self.dfa1_minus_dfa2 = configuration['DFA1_MINUS_DFA2']
        self.handler = configuration['HANDLER']

    def getresult(self):
        """
        Returns the bypass string
        Args:
            None
        Returns:
            str: The bypass string
        """
        return  "Bypass", self.bypass

    def terminate(self):
        """
        This function should be overridden
        for SIGINT purposes in case that
        membership queries allocated resources
        """
        print 'SIGINT received. Terminating processes'
        pass


    def learn(self):
        """Initiates learning algorithm"""
        if self.mma != None and self.seed_file_type != "GRAMMAR":
            return super(SFADiff, self).learn_sfa(self.mma)
        else:
            return super(SFADiff, self).learn_sfa()

    def query(self, input_string):
        """
        The function that performs the query and should be
        overriden
        Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            bool: the output of the target Mealy Machine on input input_string.
        """
        return self.handler.query(input_string)

    def _membership_query(self, input_string):
        """
        Consume the string input_string on the target machine (self.tmm)
        Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            bool: the output of the target Mealy Machine on input input_string.
        """
        if input_string in self.cache_membership:
            self.cache_membership_queries = self.cache_membership_queries + 1
            return self.cache_membership[input_string]
        self.membership_queries = self.membership_queries + 1
        output = self.query(input_string)
        self.cache_membership[input_string] = output
        return output


    def _equivalence_query(self, mmb):
        """
        Performs the equivalence query, by exchanging the learned models,
        and using the foreign model for the equivalence. If no counter
        example exists, then the algorithm falls back to the classic
        equivalence using the input automaton.
        Args:
            mmb (DFA): The input automaton
        Returns:
            str: Counter example
        """

        mmb = mmb.concretize()
        while 1:
            counterexamples = []

            # Synchronization Step: IDS sends model to Browser.
            # Browser performs RCADIFF (or two-way DIFF)
            # and either terminates (diff found) or returns
            # the counterexamples (improve models)

            if self.cross == 1:

                # Only first node will count equivalence queries

                self.equivalence_queries = self.equivalence_queries + 1

                cross_mm = None

                # Browser now waits for IDS
                self.shared_memory[0].recv()

                # receive IDS model and membership function access

                cross_mm = self.shared_memory[3]
                crossmm = _DFA(self.alphabet)
                crossmm.init_from_acceptor(cross_mm)
                other = self.shared_memory[5]
                self.ids_membership_queries = self.shared_memory[2][0]
                self.ids_cache_membership_queries = self.shared_memory[2][1]
                self.ids_equivalence_queries = self.shared_memory[2][2]
                self.ids_cache_equivalence_queries = self.shared_memory[2][3]
                self.ids_equivalence_queries_cached_membership = self.shared_memory[2][4]
                self.browserstates = len(list(mmb.states))
                self.ids_states = len(list(cross_mm.states))

                # RCADIFF

                self.cross_check_times = self.cross_check_times + 1
                # ops = _RCADiff(mma, cross_mm, self.alphabet, self.left, self.right)
                # counterexamples = ops.run()

                counterexamples = rca_diff(mmb, cross_mm, self.alphabet, self.num_diff, self.dfa1_minus_dfa2)

                # End of RCADIFF

                # _check for diff

                for string in counterexamples:
                    if string and string != "":
                        checkbrowser = self._membership_query(string)
                        checkids = other._membership_query(string)
                        if (checkbrowser and not checkids) \
                                or (not self.dfa1_minus_dfa2 and (not checkbrowser and checkids)):
                            # A vulnerability was successfully found. Inform IDS to terminate

                            self.shared_memory[0].send(["IDSTERMINATE"])
                            # Browser now waits for IDS
                            self.bypass = string

                            return True, None

                # No diff was found, Browser sends counterexamples (if exist) to IDS

                self.shared_memory[0].send(counterexamples)

            if self.cross == 2:
                # IDS sends a model to Browser
                self.shared_memory[2] = [
                    self.membership_queries,
                    self.cache_membership_queries,
                    self.equivalence_queries,
                    self.cache_equivalence_queries,
                    self.equivalence_queries_cached_membership]
                self.shared_memory[3] = mmb.copy()
                self.shared_memory[1].send(["BROWSERPROCEED"])
                # IDS now waits for Browser

                counterexamples = self.shared_memory[1].recv()
                if counterexamples[0] == "IDSTERMINATE":
                    # The IDS was instructed to terminate
                    exit(1)
                counterexamples = list(reversed(counterexamples))

            # Browser and IDS examine the counterexampes and improve their model

            update = ''
            for string in counterexamples:
                if string and string != '':
                    if (self._membership_query(string) and \
                                    mmb.consume_input(string) != True) \
                            or (not self._membership_query(string) \
                                        and mmb.consume_input(string) == True):
                        update = string
                        self.cache_equivalence.append(update)
                        break

            # If no counterexample was found, and the models are equal,
            # cached data is used to self-improve the models


            # First check that our model did not learn anything wrong,
            # when making the abstraction, by testing all the cached memberships
            if update == '':
                for string in self.cache_membership:
                    if (mmb.consume_input(string) != True and self._membership_query(string)) \
                            or (mmb.consume_input(string) == True and not self._membership_query(string)):
                        self.equivalence_queries_cached_membership += 1
                        update = string
                        break

            # Then check that the model complies with all previous cached
            # equivalence queries
            if update == '':
                for string in self.cache_equivalence:
                    if (mmb.consume_input(string) != True and self._membership_query(string)) \
                            or (mmb.consume_input(string) == True and not self._membership_query(string)):
                        self.cache_equivalence_queries += 1
                        update = string
                        break

            # If no counterexample was found, and the models are equal, classic
            # equivalence is used to self-improve the models
            if update == '':
                status, string = self._classic_equivalence_query(mmb)
                if status == False:
                    update = string

            if update != '':
                if self.cross == 1:
                    message = self.shared_memory[0].recv()
                    #ignore
                    self.shared_memory[0].send(["IDSPROCEED"])
                else:
                    self.shared_memory[1].send(["IDSREFINES"])
                    message = self.shared_memory[1].recv()
                    #ignore
                return  False, update
            else:
                if self.cross == 1:
                    message = self.shared_memory[0].recv()
                    if message[0] == "IDSNOREFINE":
                        self.shared_memory[0].send(["IDSTERMINATE"])
                        return True, None
                    elif message[0] == "IDSREFINES":
                        self.shared_memory[0].send(["IDSPROCEED"])
                        pass
                else:
                    self.shared_memory[1].send(["IDSNOREFINE"])
                    message = self.shared_memory[1].recv()
                    if message[0] == "IDSTERMINATE":
                        return True, None
                    elif message[0] == "IDSPROCEED":
                        pass

    def _classic_equivalence_query(self, mmb):
        """
        Args:
            mmb (DFA): The equivalence
        Returns:
            tuple (bool, string): A tuple (found, ce) where found is a boolean
            value that denote whether the machine given is correct. If found is
            True then the second part of the tuple is ignored. In case found is
            False, ce should be a string in which the target machine and the
            conjectured machine give different outputs.
        """
        # mm.save('conjecture{}.dfa'.format(self.equivalenceQueries))
        if not self.mmac:
            return True, None
        for string in self.cache_equivalence:
            if mmb.consume_input(string) != self.mmac.consume_input(string):
                self.cache_equivalence_queries += 1
                return False, string
        self.equivalence_queries = self.equivalence_queries + 1
        mmc = self.mmac.diff(mmb)
        string = mmc.shortest_string()
        if string and string not in self.cache_equivalence and self._membership_query(
                string):
            # print 'lets check '+input_string
            assert mmb.consume_input(string) != self.mmac.consume_input(string), \
                "Counterexample production failed  mm(input_string):{} " \
                "self.M(input_string):{}".format(
                    mmb.consume_input(string), self.mmac.consume_input(string))
            self.cache_equivalence.append(string)
            return False, string

        return True, None



    def stats(self):
        """Prints execution statistics"""
        return [
            ('Target A Membership Queries', repr(self.membership_queries)),
            ('Target A Cached Membership Queries', repr(self.cache_membership_queries)),
            ('Target A Equivalence Queries', repr(self.equivalence_queries)),
            ('Target A Cached Equivalence Queries', repr(self.cache_equivalence_queries)),
            ('Target A Cached Membership Equivalence Queries', repr(self.equivalence_queries_cached_membership)),
            ('Target B Membership Queries', repr(self.ids_membership_queries)),
            ('Target B Cached Membership Queries', repr(self.ids_cache_membership_queries)),
            ('Target B Equivalence Queries', repr(self.ids_equivalence_queries)),
            ('Target B Cached Equivalence Queries', repr(self.ids_cache_equivalence_queries)),
            ('Target B Cached Membership Equivalence Queries', repr(self.ids_equivalence_queries_cached_membership)),
            ('Learned Target B model states', repr(self.ids_states)),
            ('Learned Target A model states', repr(self.browserstates)),
            ('Cross-check times', repr(self.cross_check_times))
        ]