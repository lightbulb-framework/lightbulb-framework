"""This module contains the GOFA algorithm"""
from sfalearn.angluin_sfa import SFALearner as _SFALearner
from symautomata.cfgpda import CfgPDA as _CfgPDA
from symautomata.dfa import DFA as _DFA
from symautomata.flex2fst import Flexparser as _Flexparser
from lightbulb.core.utils.common import accept_bool, save_model, findlibrary
from lightbulb.core.base import createalphabet

META = {
    'author': 'George Argyros, Ioannis Stais',
    'name': 'GOFA',
    'description': 'Grammar Oriented Filter Auditing',
    'type': 'CORE',
        'options': [
            ('ALPHABET', None, True, 'File containing the alphabet'),
            ('SEED_FILE', None, False, 'File containting regular expressions/grammar'),
            ('SEED_FILE_TYPE', "FLEX", False, 'File type (e.g FLEX, GRAMMAR, FST)'),
            ('TESTS_FILE', None, True, 'File containting regular expressions/grammar'),
            ('TESTS_FILE_TYPE', "FLEX", True, 'File type (e.g FLEX, GRAMMAR, FST)'),
            ('SAVE', False, False, 'File to save learned filter if no bypass is found'),
            ('HANDLER', None, True, 'Handler for membership query function'),
       ],
    'comments': ['An algorithm that infers symbolic representations '
                 'of automata in the standard membership/equivalence'
                 'query model.']
}

class GOFA(_SFALearner):
    """GOFA algorithm module"""

    def __init__(self, configuration):
        self.setup(configuration)
        if not self.alphabet or isinstance(self.alphabet, str):
            self.alphabet = createalphabet(self.alphabet)
        super(GOFA, self).__init__(self.alphabet)
        self.membership_queries = 0
        self.cache_membership_queries = 0
        self.equivalence_queries = 0
        self.cache_equivalence_queries = 0
        self.cache_equivalence = []
        self.cache_membership = {}
        self.mma = None
        self.mmac = None
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
        self.save = configuration['SAVE']
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

    def learn(self):
        """Initiates learning algorithm"""
        if self.mma != None and self.seed_file_type != "GRAMMAR":
            return super(GOFA, self).learn_sfa(self.mma)
        else:
            return super(GOFA, self).learn_sfa()

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
        Consume the string input_string on the target machine
        Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            str: the output of the target Mealy Machine on input input_string.
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
        Args:
            mmb (DFA): The equivalence
        Returns:
            tuple (bool, string): A tuple (found, ce) where found is a boolean
            value that denote whether the machine given is correct. If found is
            True then the second part of the tuple is ignored. In case found is
            False, ce should be a string in which the target machine and the
            conjectured machine give different outputs.
        """
        mmb = mmb.concretize()
        # mm.save('conjecture{}.dfa'.format(self.equivalenceQueries))
        for string in self.cache_equivalence:
            if not mmb.consume_input(string):
                self.cache_equivalence_queries += 1
                return False, string

        self.equivalence_queries = self.equivalence_queries + 1
        mmc = self.mmac.diff(mmb)
        string = None
        if mmc:
            string = mmc.shortest_string()
        if string:
            assert mmb.consume_input(string) != self.mmac.consume_input(string), \
                "Counterexample production failed  mm(input_string):{}" \
                " self.M(input_string):{}".format(
                    mmb.consume_input(string), self.mmac.consume_input(string))
            if not self._membership_query(string):
                self.bypass = string
                return True, None
            self.cache_equivalence.append(string)
            return False, string
        return True, None



    def stats(self):
        """Prints execution statistics"""
        stats = [
            ('Membership Queries', repr(self.membership_queries)),
            ('Cached Membership Queries', repr(self.cache_membership_queries)),
            ('Equivalence Queries ', repr(self.equivalence_queries)),
            ('Cached Equivalence Queries ', repr(self.cache_equivalence_queries))]
        save = None
        if self.save and self.save != "False" and not self.bypass:
            stats.append((save_model(self.save, self.get_sfa_conjecture().concretize())))
        return stats
