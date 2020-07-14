"""This module creates a PDA from a CNF """
from pda import PDA, PDAState


class ProdStruct:
    """This class is used as a struct for each CNF rule"""
    type = 0
    a = 0
    b0 = 0
    b1 = 0

    def __init__(self):
        """ Initialization class """
        pass


class CnfPda:
    """This class creates a PDA from a CNF"""
    def __init__(self, alphabet):
        """
        Args:
            alphabet (list): The input alphabet
        """
        self.alphabet = alphabet


    def _mkpda(self, nonterms, productions, productions_struct, terminals, splitstring=1):
        """
        This function generates a PDA from a CNF grammar as described in:
          -  http://www.oit.edu/faculty/sherry.yang/CST229/Lectures/7_pda.pdf
          -  http://www.eng.utah.edu/~cs3100/lectures/l18/pda-notes.pdf

        If all of the grammar productions are in the Chomsky Normal Form,
        then follow the template for constructing a pushdown symautomata:

        1. Start
        2. Push S
        3. Pop
        4. Case:
            Nonterminal A: For every production rule of this form: A: BC, Push C and then Push B

        Args:
             nonterms (list): Non terminals list
             productions (dict): productions in the CNF form:
                                    A -> a or A -> b0b1, or S -> e
             productions_struct (dict):  productions in the CNF form in structure form
                                    object.a for A -> a,
                                    object.b0 and object.b1 for A -> b0b1
                                    and object.type where type is
                                        1 for A-->a and 2 for A-->b0b1
             terminals (list): All terminals
             splitstring (bool): If enabled an extra space is added after each symbol.
        Returns:
            PDA: The generated PDA
        """
        pda = PDA(self.alphabet)
        pda.nonterminals = nonterms
        pda.terminals = terminals

        pda.s[pda.n] = PDAState()
        pda.s[pda.n].id = pda.n
        pda.s[pda.n].sym = '@closing'
        pda.s[pda.n].type = 1
        pda.s[pda.n].trans[1] = [0]

        pda.n = pda.n + 1
        pda.s[pda.n] = PDAState()
        pda.s[pda.n].id = pda.n
        pda.s[pda.n].type = 1
        pda.s[pda.n].sym = nonterms[0]
        pda.s[pda.n].trans[2] = [0]

        pda.n = pda.n + 1
        pda.s[pda.n] = PDAState()
        pda.s[pda.n].id = pda.n
        pda.s[pda.n].type = 2
        pda.s[pda.n].trans[0] = ['@closing']

        counter = 0
        i = 0
        while i < len(nonterms):
            j = 0
            while j < len(productions[nonterms[i]]):
                if productions_struct[counter].type == 1:
                    # ADD AND CONNECT STATE
                    pda.n = pda.n + 1
                    pda.s[pda.n] = PDAState()
                    pda.s[pda.n].id = pda.n
                    if pda.n not in pda.s[2].trans:
                        pda.s[2].trans[pda.n] = []
                    pda.s[2].trans[pda.n].append(nonterms[i])

                    if splitstring == 0:

                        # FILL NEW STATE  READ
                        pda.s[pda.n].type = 3
                        pda.s[pda.n].trans[2] = [productions_struct[counter].a]

                    else:
                        # THE FOLLOWIN SWITCH IS DUE TO THE REQUIREMENT OF
                        # HAVING STRINGS SPLITTED TO SYMBOLS AND CAN INTERSECT
                        # WITH DFA

                        if productions_struct[counter].a not in terminals or \
                                        len(productions_struct[counter].a) == 1:
                            # FILL NEW STATE  READ
                            pda.s[pda.n].type = 3
                            pda.s[pda.n].trans[pda.n + 1] = [productions_struct[counter].a.lower()]
                            pda.n = pda.n + 1
                            pda.s[pda.n] = PDAState()
                            pda.s[pda.n].id = pda.n
                            pda.s[pda.n].type = 3
                            pda.s[pda.n].trans[2] = [' ']

                        else:
                            pda.s[pda.n].type = 3
                            pda.s[pda.n].trans[pda.n + 1] = \
                                [productions_struct[counter].a[0].lower()]
                            k = 1
                            while k < len(productions_struct[counter].a) - 1:
                                pda.n = pda.n + 1
                                pda.s[pda.n] = PDAState()
                                pda.s[pda.n].id = pda.n
                                pda.s[pda.n].type = 3
                                pda.s[pda.n].trans[pda.n +1] = \
                                    [productions_struct[counter].a[k].lower()]
                                k = k + 1
                            pda.n = pda.n + 1
                            pda.s[pda.n] = PDAState()
                            pda.s[pda.n].id = pda.n
                            pda.s[pda.n].type = 3

                            pda.s[pda.n].trans[pda.n + 1] = \
                                [productions_struct[counter].a[-1].lower()]
                            pda.n = pda.n + 1
                            pda.s[pda.n] = PDAState()
                            pda.s[pda.n].id = pda.n
                            pda.s[pda.n].type = 3
                            pda.s[pda.n].trans[2] = [' ']

                else:
                    # ADD AND CONNECT PUSH STATE
                    pda.n = pda.n + 1
                    pda.s[pda.n] = PDAState()
                    pda.s[pda.n].id = pda.n
                    if pda.n not in pda.s[2].trans:
                        pda.s[2].trans[pda.n] = []
                    pda.s[2].trans[pda.n].append(nonterms[i])

                    # FILL NEW STATE
                    pda.s[pda.n].type = 1
                    pda.s[pda.n].sym = productions_struct[counter].b1
                    pda.s[pda.n].trans[(pda.n) + 1] = [0]

                    # ADD AND CONNECT PUSH STATE (ALREADY CONNECTED)
                    pda.n = pda.n + 1
                    pda.s[pda.n] = PDAState()
                    pda.s[pda.n].id = pda.n

                    # FILL NEW STATE
                    pda.s[pda.n].type = 1
                    pda.s[pda.n].sym = productions_struct[counter].b0
                    pda.s[pda.n].trans[2] = [0]

                j = j + 1
                counter = counter + 1

            i = i + 1
        return pda

    def initialize(
            self,
            nonterminal,
            productions,
            terminals,
            splitstring=1):
        """

        productions in structure form <1> A-->b , <2> a-->BC
        """
        cnt = 0
        i = 0
        productions_struct = {}
        while i < len(nonterminal):
            j = 0
            while j < len(productions[nonterminal[i]]):
                productions_struct[cnt] = ProdStruct()
                if 'a' in productions[nonterminal[i]][j]:
                    productions_struct[cnt].type = 1
                    productions_struct[cnt].a = productions[nonterminal[i]][j]['a']

                else:
                    productions_struct[cnt].type = 2
                    productions_struct[cnt].b0 = productions[nonterminal[i]][j]['b0']
                    productions_struct[cnt].b1 = productions[nonterminal[i]][j]['b1']
                cnt = cnt + 1
                j = j + 1
            i = i + 1
        return self._mkpda(
            nonterminal,
            productions,
            productions_struct,
            terminals,
            splitstring)
