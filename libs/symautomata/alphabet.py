import os.path
"""This module configures that alphabet."""


def _load_alphabet(filename):
    """
    Load a file containing the characters of the alphabet.
    Every unique character contained in this file will be used as a symbol
    in the alphabet.
    """
    with open(filename, 'r') as f:
        return list(set(f.read()))

def createalphabet(alphabetinput=None):
    """
    Creates a sample alphabet containing printable ASCII characters
    """
    if alphabetinput and os.path.isfile(alphabetinput):
        return _load_alphabet(alphabetinput)
    elif alphabetinput:
        alpha = []
        setlist = alphabetinput.split(',')
        for alphaset in setlist:
            a = int(alphaset.split('-')[0])
            b = int(alphaset.split('-')[1])
            for i in range(a, b):
                alpha.append(str(unichr(i)))
        return alpha
    alpha = []
    for i in range(32, 127):
        alpha.append(str(unichr(i)))
    return alpha