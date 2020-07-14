"""This module generates a PDA using a CFG as input"""
from cnfpda import CnfPda
from cfggenerator import CNFGenerator

class CfgPDA():
    """Create a PDA from a CFG"""

    def __init__(self, alphabet=None):
        """
        Initialize values
        Args:
            alphabet (list): The input alphabet
        Returns:
            None
        """
        self.alphabet = alphabet

    def _extract_alphabet(self, grammar):
        """
        Extract an alphabet from the given grammar.
        """
        alphabet = set([])
        for terminal in grammar.Terminals:
            alphabet |= set([x for x in terminal])
        self.alphabet = list(alphabet)

    def _read_file(self, fname):
        """
        Read file containing CFG
        Args:
            fname (str): The file name
        Returns:
            list: The list of CFG rules
        """
        with open(fname) as input_file:
            re_grammar = [x.strip('\n') for x in input_file.readlines()]
        return re_grammar

    def _mpda(self, re_grammar, splitstring=0):
        """
        Args:
            re_grammar (list): A list of grammar rules
            splitstring (bool): A boolean for enabling or disabling
                            the splitting of symbols using a space
        Returns:
            PDA: The generated PDA
        """
        cnfgrammar = CNFGenerator(re_grammar)

        if not self.alphabet:
            self._extract_alphabet(cnfgrammar)

        cnftopda = CnfPda(self.alphabet)
        productions = {}
        nonterminals = []
        nonterminals.append(cnfgrammar.init_symbol)
        for key in list(cnfgrammar.grammar_nonterminals):
            if key != cnfgrammar.init_symbol:
                nonterminals.append(key)
        for key in list(cnfgrammar.grammar_nonterminals):
            j = 0
            productions[key] = {}
            # print 'testing '+key
            for pair in cnfgrammar.grammar_rules:
                cnf_form = list(pair)
                if cnf_form[0] == key:
                    productions[key][j] = {}
                    if isinstance(cnf_form[1], type(())):
                        #            print list(p[1])
                        productions[key][j]['b0'] = list(cnf_form[1])[0]
                        productions[key][j]['b1'] = list(cnf_form[1])[1]
                    else:
                        #           print p[1]
                        productions[key][j]['a'] = cnf_form[1]
                    j = j + 1
        return cnftopda.initialize(
            nonterminals, productions, list(
                cnfgrammar.grammar_terminals), splitstring)

    def yyparse(self, cfgfile, splitstring=0):
        """
        Args:
            cfgfile (str): The path for the file containing the CFG rules
            splitstring (bool): A boolean for enabling or disabling
                            the splitting of symbols using a space
        Returns:
            PDA: The generated PDA
        """
        re_grammar = self._read_file(cfgfile)
        mma = self._mpda(re_grammar, splitstring)
        return mma
