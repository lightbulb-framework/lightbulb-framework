"""
This module performs all basic PDA operations.
It is an interface for push down automata.
"""


class PDAState(object):
    """This is the structure for a PDA state"""
    type = 0
    sym = 0
    trans = None
    id = 0

    def printer(self):
        """Prints PDA state attributes"""
        print " ID " + repr(self.id)
        if self.type == 0:
            print " Tag: - "
            print " Start State - "
        elif self.type == 1:
            print " Push " + repr(self.sym)
        elif self.type == 2:
            print " Pop State " + repr(self.sym)
        elif self.type == 3:
            print " Read State " + repr(self.sym)
        elif self.type == 4:
            print " Stop State " + repr(self.sym)
        for j in self.trans:
            if len(self.trans[j]) > 1 or (len(self.trans[j]) == 1):
                for symbol in self.trans[j]:
                    print " On Symbol " + repr(symbol) + " Transition To State " + repr(j)

    def __init__(self):
        """State Initialization"""
        self.trans = {}


class syms:
    """The DFA accepted symbols"""

    def __init__(self):
        """Initialize symbols"""
        self.symbols = {}
        self.reversesymbols = {}

    def __getitem__(self, char):
        """
        Finds a symbol identifier based on the input character
        Args:
            char (str): The symbol character
        Returns:
            int: The retrieved symbol identifier
        """
        return self.reversesymbols[char]

    def __setitem__(self, char, num):
        """
        Sets a symbol
        Args:
            char (str): The symbol character
            num (int): The  symbol identifier
        Returns:
           None
        """
        self.symbols[num] = char
        self.reversesymbols[char] = num

    def find(self, num):
        """
        Finds a symbol based on its identifier
        Args:
            num (int): The symbol identifier
        Returns:
            str: The retrieved symbol
        """
        return self.symbols[num]

    def items(self):
        """Returns all stored symbols
        Args:
            None
        Returns:
            dict:The included symbols
        """
        return self.symbols

class PythonPDA(object):
    """This is the structure for a PDA"""
    n = 0
    s = None
    accepted = None
    terminals = None
    nonterminals = None


    def printer(self):
        """Prints PDA states and their attributes"""
        i = 0
        while i < self.n + 1:
            print "--------- State No --------" + repr(i)
            self.s[i].printer()
            i = i + 1

    def consume_input(self, mystr, stack=[], state=1, curchar=0, depth=0):
        """
        Consumes an input and validates if it is accepted
        Args:
            mystr (str): the input string to be consumes
            stack (list): the stack of symbols
            state (int): the current state of the PDA
            curchar (int): the index of the consumed character
            depth (int): the depth of the function call in the stack
        Returns:
            bool: A value indicating the correct or erroneous execution
        """
        mystrsplit = mystr.split(' ')
        if self.s[state].type == 1:
            stack.append(self.s[state].sym)
            if len(self.s[state].trans) > 0:
                state = self.s[state].trans[0]
                if self.parse(
                        mystr,
                        stack=stack,
                        state=state,
                        curchar=curchar,
                        depth=depth + 1) == 1:
                    return True
            return False
        if self.s[state].type == 2:
            if len(stack) == 0:
                return False
            sym = stack.pop()
            for key in self.s[state].trans:
                if sym in self.s[state].trans[key]:
                    if self.parse(
                            mystr,
                            stack=stack,
                            state=key,
                            curchar=curchar,
                            depth=depth + 1) == 1:
                        return True
            return False
        if self.s[state].type == 3:
            for key in self.s[state].trans:
                if mystrsplit[curchar] in self.s[state].trans[key]:
                    # print 'found '
                    if curchar + 1 == len(mystrsplit) \
                            and 'closing' in self.s[key].trans:
                        return True
                    elif curchar + 1 == len(mystrsplit):
                        return False

                    # print 'lets try as next state the state ' + repr(key)
                    if self.parse(
                            mystr,
                            stack=stack,
                            state=key,
                            curchar=curchar + 1,
                            depth=depth + 1) == 1:
                        return True
            return False


    def __init__(self, alphabet):
        """
        Args:
            alphabet (list): the input alphabet
        Returns:
            None
        """
        self.s = {}
        self.alphabet = alphabet

        num = 1
        self.isyms = syms()
        self.osyms = syms()
        for char in alphabet:
            self.isyms.__setitem__(char, num)
            self.osyms.__setitem__(char, num)
            num = num + 1