from symautomata.dfa import DFA
from symautomata.flex2fst import Flexparser
from symautomata.alphabet import createalphabet
from lightbulb.core.utils.common import save_model, findlibrary
import json

META = {
    'author': 'George Argyros, Ioannis Stais',
    'description': 'Perform automata operations on learned models or flex files',
    'type':'Distinguisher',
    'options': [
        ('FILE_A', None, True, 'Model A'),
        ('FILE_TYPE_A', "FST", True, 'Possible values: FST, FLEX'),
        ('FILE_B', None, False, 'Model B'),
        ('FILE_TYPE_B', "FST", False, 'Possible values: FST, FLEX'),
        ('OPERATION', None, False, 'Possible values: INTERSECT, UNION, DIFFERENCE, COMPLEMENT, None'),
        ('ALPHABET', None, False, 'File containing the alphabet'),
        ('RESULT', None, False, 'Possible values: STRING, REGEX, or a file path to save model'),
    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}



class Module():


    def __init__(self, configuration):
        self.mma = self.read_file(findlibrary(configuration['FILE_A']), findlibrary(configuration['FILE_TYPE_A']))
        self.states_a = len(self.mma)
        self.mmb = self.read_file(findlibrary(configuration['FILE_B']), findlibrary(configuration['FILE_TYPE_B']))
        self.states_b = len(self.mmb)
        self.mmc = None
        self.operation = configuration['OPERATION']
        self.result = configuration['RESULT']
        self.alphabet = createalphabet(configuration['ALPHABET'])
        pass

    def read_file(self, file, file_type):
        if file is not None and file_type is not None:
            if file_type == "FLEX":
                flex_object_m = Flexparser(self.alphabet)
                mma = flex_object_m.yyparse(file)
                mma.minimize()
            elif file_type == "FST":
                mma = DFA(self.alphabet)
                mma.load(file)
                mma.minimize()
            return mma
        return None

    def learn(self):
        if self.operation == "COMPLEMENT":
            self.mma.complement(self.alphabet)
            self.mmc = self.mma
        elif self.operation == "INTERSECT" and self.mmb != None:
            self.mmc = self.mma & self.mmb
        elif self.operation == "UNION" and self.mmb != None:
            self.mmc = self.mma | self.mmb
            self.mmc = self.mmc.determinize()
        elif self.operation == "DIFFERENCE" and self.mmb != None:
            self.mmc = self.mma.diff(self.mmb)
        else:
            self.mmc = self.mma
        self.mmc.minimize()
        self.states_c = len(self.mmc)
        pass

    def stats(self):
        return  [("FILE_A States", self.states_a),
                 ("FILE_B States", self.states_b),
                 ("FILE_C States", self.states_c)]


    def getresult(self):
        return save_model(self.result, self.mmc)
