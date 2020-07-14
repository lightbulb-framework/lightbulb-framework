"""This module performs the angluin algorithm"""

#!/usr/bin/python

import logging
from itertools import product
from os.path import commonprefix

from symautomata.mealy import MealyMachine


class _ObservationTable:
    def __init__(self, alphabet):
        """
        Initialization function
        Args:
            alphabet (list): input alphabet
        Returns:
            None
        """
        self.observation_table = {}
        self.sm_vector = []
        self.smi_vector = []
        self.em_vector = list(alphabet)
        self.alphabet = list(alphabet)
        self.equiv_classes = {}

    def is_closed(self):
        """
        _check if the observation table is closed.
        Args:
            None
        Returns:
            tuple (bool, str): True if the observation table is
            closed and false otherwise. If the table is not closed
            the escaping string is returned.
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
            key (tuple (str,str)): A tuple specifying the row and column of the table
        Returns:
            str: The observation table entry
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


class MealyMachineLearner(object):
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

    def __init__(self, alphabet, _, loglevel=logging.DEBUG, logfile='angluin_fst.log'):
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
                            format='%(asctime)input_string:%(levelname)input_string: '
                                   '%(message)input_string',
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

        @rtype: String
        @return: the output of the target Mealy Machine on input input_string.
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
        raise NotImplementedError(
            'Equivalence Query method is not implemented')

    def _fill_table_entry(self, row, col):
        """""
        Fill an entry of the observation table.
        Args:
            row (str): The row of the observation table
            col (str): The column of the observation table
        Returns:
            None
        """
        prefix = self._membership_query(row)
        full_output = self._membership_query(row + col)
        length = len(commonprefix([prefix, full_output]))
        self.observation_table[row, col] = full_output[length:]

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
        for i in range(index):
            for arc in state:
                if mma.isyms.find(arc.ilabel) == w_string[i]:
                    state = mma[arc.nextstate]
                    s_index = arc.nextstate

        # The id of the state is its index inside the Sm list
        access_string = self.observation_table.sm_vector[s_index]
        logging.debug(
            'Access string for %d: %s - %d ',
            index,
            access_string,
            s_index)

        return access_string

    def _check_suffix(self, w_string, access_string, index):
        """
        Checks if access string suffix matches with the examined string suffix
        Args:
            w_string (str): The examined string to be consumed
            access_string (str): The access string for the state
            index (int): The index value for selecting the prefix of w
        Returns:
            bool: A boolean valuei indicating if matching was successful
        """
        prefix_as = self._membership_query(access_string)
        full_as = self._membership_query(access_string + w_string[index:])

        prefix_w = self._membership_query(w_string[:index])
        full_w = self._membership_query(w_string)

        length = len(commonprefix([prefix_as, full_as]))
        as_suffix = full_as[length:]

        length = len(commonprefix([prefix_w, full_w]))
        w_suffix = full_w[length:]

        if as_suffix != w_suffix:
            logging.debug('Access string state incorrect')
            return True
        logging.debug('Access string state correct.')
        return False

    def _find_bad_transition(self, mma, w_string):
        """
        Checks for bad DFA transitions using the examined string
        Args:
            mma (DFA): The hypothesis automaton
            w_string (str): The examined string to be consumed
        Returns:
            str: The prefix of the examined string that matches
        """
        conj_out = mma.consume_input(w_string)
        targ_out = self._membership_query(w_string)
        # TODO: handle different length outputs from conjecture and target
        # hypothesis.
        length = min(len(conj_out), len(targ_out))
        diff = [i for i in range(length)
                if conj_out[i] != targ_out[i]]
        if len(diff) == 0:
            diff_index = len(targ_out)
        else:
            diff_index = diff[0]

        low = 0
        high = len(w_string)
        while True:
            i = (low + high) / 2
            length = len(self._membership_query(w_string[:i]))
            if length == diff_index + 1:
                return w_string[:i]
            elif length < diff_index + 1:
                low = i + 1
            else:
                high = i - 1

    def _process_counter_example(self, mma, w_string):
        """"
       Process a counterexample in the Rivest-Schapire way.
       Args:
           mma (DFA): The hypothesis automaton
           w_string (str): The examined string to be consumed
       Returns:
           None
        """
        w_string = self._find_bad_transition(mma, w_string)

        diff = len(w_string)
        same = 0
        while True:
            i = (same + diff) / 2
            access_string = self._run_in_hypothesis(mma, w_string, i)
            is_diff = self._check_suffix(w_string, access_string, i)
            if is_diff:
                diff = i
            else:
                same = i
            if diff - same == 1:
                break
        exp = w_string[diff:]

        self.observation_table.em_vector.append(exp)
        for row in self.observation_table.sm_vector + self.observation_table.smi_vector:
            self._fill_table_entry(row, exp)

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

    def get_mealy_conjecture(self):
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
        mma = MealyMachine()
        for s in self.observation_table.sm_vector:
            for i in self.alphabet:
                dst = self.observation_table.equiv_classes[s + i]
                # If dst == None then the table is not closed.
                if dst is None:
                    logging.debug('Conjecture attempt on non closed table.')
                    return None
                o = self.observation_table[s, i]
                src_id = self.observation_table.sm_vector.index(s)
                dst_id = self.observation_table.sm_vector.index(dst)
                mma.add_arc(src_id, dst_id, i, o)

        # This works only for Mealy machines
        for s in mma.states:
            s.final = True
        return mma

    def _init_table(self):
        """
        Initialize the observation table.
        """
        self.observation_table.sm_vector.append('')
        self.observation_table.smi_vector = list(self.alphabet)
        self.observation_table.em_vector = list(self.alphabet)

        for i in self.observation_table.em_vector:
            self._fill_table_entry('', i)

        for s, e in product(self.observation_table.smi_vector, self.observation_table.em_vector):
            self._fill_table_entry(s, e)

    def learn_mealy_machine(self):
        """
        Implements the high level loop of the algorithm for learning a
        Mealy machine.
        Args:
            None
        Returns:
            MealyMachine: The learned mealy machine
        """
        logging.info('Initializing learning procedure.')
        self._init_table()

        logging.info('Generating a closed and consistent observation table.')
        while True:

            closed = False
            # Make sure that the table is closed and consistent
            while not closed:

                logging.debug('Checking if table is closed.')
                closed, string = self.observation_table.is_closed()
                if not closed:
                    logging.debug('Closing table.')
                    self._ot_make_closed(string)
                else:
                    logging.debug('Table closed.')

            # Create conjecture
            mma = self.get_mealy_conjecture()

            logging.info('Generated conjecture machine with %d states.',
                         len(list(mma.states)))

            # _check correctness
            logging.debug('Running equivalence query.')
            found, counter_example = self._equivalence_query(mma)

            # Are we done?
            if found:
                logging.info('No counterexample found. Hypothesis is correct!')
                break

            # Add the new experiments into the table to reiterate the
            # learning loop
            logging.info(
                'Processing counterexample %input_string with length %d.',
                counter_example,
                len(counter_example))
            self._process_counter_example(mma, counter_example)

        logging.info('Learning complete.')
        return mma


if __name__ == '__main__':
    print 'Angluin Algorithm for learning Mealy Machines abstract \
            class implementation.'
