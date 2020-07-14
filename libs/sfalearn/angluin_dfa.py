"""This module performs the angluin algorithm"""
#!/usr/bin/python

import logging
from observationtableinit import ObservationTableInit

from symautomata.dfa import DFA


class _ObservationTable:
    def __init__(self, alphabet):
        """
        Args:
            alphabet (list): input alphabet
        Returns:
            None
        """
        self.observation_table = {}
        self.sm_vector = []
        self.smi_vector = []
        self.em_vector = []
        self.alphabet = list(alphabet)
        self.equiv_classes = {}

    def is_closed(self):
        """
        _check if the observation table is closed.
        Args:
            None
        Returns:
            tuple (bool, str): True if the observation table is closed and false otherwise.
                                If the table is not closed the escaping string is returned.
        """
        for t in self.smi_vector:
            found = False
            for s in self.sm_vector:
                if self.observation_table[s] == self.observation_table[t]:
                    self.equiv_classes[t] = s
                    found = True
                    break
            if not found:
                return False, t
        return True, None

    def __getitem__(self, key):
        """
        Return an entry from the observation table
        Args:
            key tuple (str,str): A tuple specifying the row and column of the table
        Returns:
            str: The entry from the observation table
        """
        row, col = key
        try:
            return self.observation_table[row][col]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        """
        Args:
            key (tuple (str,str)): row and column of the table
            value (str): entry from the observation table
        Returns:
            None
        """
        row, col = key
        if row not in self.observation_table:
            self.observation_table[row] = {}
        self.observation_table[row][col] = value


class DFALearner(object):
    """
    Implements the algorithm for learning Mealy Machines (i.e. deterministic
    finite state transducers) as described in the paper
    - Inferring Mealy machines

    The method getMealyMachine is the main method which implements the
    aforementioned algorithm.

    The class itself is an abstract class and it will fail if anyone tries to
    invoke it directly. In order to use the class on should inherit a new
    class from it and define the abstract methods _membership_query and
    _equivalence_query.

    Please refer into the method definitions for more details on the methods.
    """
    epsilon = ''

    def __init__(self, alphabet, loglevel=logging.INFO, logfile='angluin_dfa.log'):
        """
        Args:
            alphabet (list): input alphabet.
            loglevel (loglevel type): The type of the logging.
            logfile (str): The file that the logs will be maintained
        Returns:
            None
        """
        # Initialize the logging for the algorithm.
        logging.basicConfig(filename=logfile,
                            format='%(asctime)s:%(levelname)s: %(message)s',
                            filemode='w',  # Overwrite any old log files
                            level=loglevel)

        # Initialize the observation table with the inpur alphabet
        self.alphabet = list(alphabet)
        self.observation_table = _ObservationTable(alphabet)

    def _membership_query(self, input_string):
        """
        Abstract method, it should implement the membership query. On input
        a string input_string the method must return the output of the target Mealy
        Machine on that string.
        Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            str: the output of the target Mealy Machine on input input_string.
        """
        raise NotImplementedError('Membership Query method is not implemented')

    def _equivalence_query(self, conj_machine):
        """
        Abstract method, it should implement equivalence query. In systems
        where an equivalence query is unavailable a search strategy should
        be implemented to search for counterexamples. In absence of a
        counterexample one should assume that the machine is correct.
        Args:
            conj_machine (MealyMachine): The Mealy Machine conjecture
        Returns:
            tuple (bool, string): A tuple (found, ce) where found is a boolean
            value that denote whether the machine given is correct. If found is
            True then the SECOND part of the tuple is ignored. In case found is
            False, ce should be a string in which the target machine and the
            conjectured machine give different outputs.
        """
        raise NotImplementedError('Equivalence Query method is not implemented')

    def _fill_table_entry(self, row, col):
        """""
        Fill an entry of the observation table.
        Args:
            row (str): The row of the observation table
            col (str): The column of the observation table
        Returns:
            None
        """
        self.observation_table[row, col] = self._membership_query(row + col)

    ###### RivSch counterexample processing #####

    def _run_in_hypothesis(self, mma, w_string, index):
        """""
        Run the string in the hypothesis automaton for index steps and then
        return the access string for the state reached concatanated with the
        rest of the string w.
        Args:
            mma (DFA): The hypothesis automaton
            w_string (str): The examined string to be consumed
            index (int): The index value for selecting the prefix of w
        Return:
            str: The access string
        """
        state = mma[0]
        s_index = 0
        for i in range(index):
            for arc in state:
                if mma.isyms.find(arc.ilabel) == w_string[i]:
                    state = mma[arc.nextstate]
                    s_index = arc.nextstate

        # The id of the state is its index inside the Sm list
        access_string = self.observation_table.sm_vector[s_index]
        logging.debug('Access string for %d: %input_string - %d ', index, access_string, s_index)
        return access_string

    def _process_counter_example(self, mma, w_string):
        """"
        Process a counterexample in the Rivest-Schapire way.
        Args:
            mma (DFA): The hypothesis automaton
            w_string (str): The examined string to be consumed
        Returns:
            None
        """
        diff = len(w_string)
        same = 0
        membership_answer = self._membership_query(w_string)
        while True:
            i = (same + diff) / 2
            access_string = self._run_in_hypothesis(mma, w_string, i)
            if membership_answer != self._membership_query(access_string + w_string[i:]):
                diff = i
            else:
                same = i
            if diff - same == 1:
                break
        exp = w_string[diff:]
        self.observation_table.em_vector.append(exp)
        for row in self.observation_table.sm_vector + self.observation_table.smi_vector:
            self._fill_table_entry(row, exp)
        return 0

    #### End of counterexample processing  #####


    def _ot_make_closed(self, access_string):
        """
        Given a state input_string in Smi that is not equivalent with any state in Sm
        this method will move that state in Sm create a corresponding Smi
        state and fill the corresponding entries in the table.
        Args:
            access_string (str): State access string
        Returns:
            None
        """
        self.observation_table.sm_vector.append(access_string)
        for i in self.alphabet:
            self.observation_table.smi_vector.append(access_string + i)
            for e in self.observation_table.em_vector:
                self._fill_table_entry(access_string + i, e)

    def get_dfa_conjecture(self):
        """
        Utilize the observation table to construct a Mealy Machine.
        The library used for representing the Mealy Machine is the python
        bindings of the openFST library (pyFST).
        Args:
            None
        Returns:
            MealyMachine: A mealy machine build based on a closed and consistent
        observation table.
        """
        dfa = DFA(self.alphabet)
        for s in self.observation_table.sm_vector:
            for i in self.alphabet:
                dst = self.observation_table.equiv_classes[s + i]
                # If dst == None then the table is not closed.
                if dst == None:
                    logging.debug('Conjecture attempt on non closed table.')
                    return None
                obsrv = self.observation_table[s, i]
                src_id = self.observation_table.sm_vector.index(s)
                dst_id = self.observation_table.sm_vector.index(dst)
                dfa.add_arc(src_id, dst_id, i, obsrv)

        # Mark the final states in the hypothesis automaton.
        i = 0
        for s in self.observation_table.sm_vector:
            dfa[i].final = self.observation_table[s, self.epsilon]
            i += 1
        return dfa

    def _init_table(self):
        """
        Initialize the observation table.
        """
        self.observation_table.sm_vector.append(self.epsilon)
        self.observation_table.smi_vector = list(self.alphabet)
        self.observation_table.em_vector.append(self.epsilon)

        self._fill_table_entry(self.epsilon, self.epsilon)
        for s in self.observation_table.smi_vector:
            self._fill_table_entry(s, self.epsilon)

    def _init_table_from_dfa(self, mma):
        """
        Args:
            mma (DFA): The input automaton
        Returns:
            None
        """
        observation_table_init = ObservationTableInit(self.epsilon, self.alphabet)
        sm_vector, smi_vector, em_vector = observation_table_init.initialize(mma)
        self.observation_table.sm_vector = sm_vector
        self.observation_table.smi_vector = smi_vector
        self.observation_table.em_vector = em_vector

        logging.info('Initialized from DFA em_vector table is the following:')
        logging.info(em_vector)

        self._fill_table_entry(self.epsilon, self.epsilon)

        for row in sorted(list(set(sm_vector + smi_vector)), key=len)[1:]:
            # list(set([])) is used to remove duplicates, [1:0] to remove epsilon
            for column in em_vector:
                self._fill_table_entry(str(row), str(column))

    def learn_dfa(self, mma=None):
        """
        Implements the high level loop of the algorithm for learning a
        Mealy machine.
        Args:
            mma (DFA): The input automaton
        Returns:
            MealyMachine: A string and a model for the Mealy machine to be learned.
        """
        logging.info('Initializing learning procedure.')
        if mma:
            self._init_table_from_dfa(mma)
        else:
            self._init_table()

        logging.info('Generating a closed and consistent observation table.')
        while True:

            closed = False
            # Make sure that the table is closed
            while not closed:
                logging.debug('Checking if table is closed.')
                closed, string = self.observation_table.is_closed()
                if not closed:
                    logging.debug('Closing table.')
                    self._ot_make_closed(string)
                else:
                    logging.debug('Table closed.')

            # Create conjecture

            dfa = self.get_dfa_conjecture()

            logging.info('Generated conjecture machine with %d states.',len(list(dfa.states)))

            # _check correctness
            logging.debug('Running equivalence query.')
            found, counter_example = self._equivalence_query(dfa)

            # Are we done?
            if found:
                logging.info('No counterexample found. Hypothesis is correct!')
                break

            # Add the new experiments into the table to reiterate the
            # learning loop
            logging.info('Processing counterexample %s with length %d.', counter_example, len(counter_example))
            self._process_counter_example(dfa, counter_example)

        logging.info('Learning complete.')
        logging.info('Learned em_vector table is the following:')
        logging.info(self.observation_table.em_vector)
        return '', dfa


if __name__ == '__main__':
    print 'Angluin Algorithm for learning Mealy Machines abstract \
            class implementation.'
