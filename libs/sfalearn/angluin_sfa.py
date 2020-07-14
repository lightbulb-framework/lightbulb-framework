""" This module performs the Angluin Algorithm for learning Symbolic Automata abstract
class implementation."""
# !/usr/bin/python

import logging
import random

from observationtableinit import ObservationTableInit
from symautomata.sfa import SFA, SetPredicate


class _ObservationTable:
    def __init__(self, alphabet):
        """
        Initialization Function for the Observation Table
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
        self.training_data = {}

    def _add_training_data(self, src, dst, symbol):
        """
        Training_data is a dictionary from strings to lists.
        - Each string (key) is an access string
        - Each list (value) is a list of tuples (target_state, [symbols directed to that
        state]). These represent that a transition exists from the state used as key to the first
        part of the training_data to the dst state which is the first part of the tuple
        with all the symbols in the list in the SECOND part of the tuple.
        Args:
            src (str): The source state
            dst (str): The target state
            symbol (str): The transition symbol
        Returns:
            None
        """
        src_data = self.training_data[src]
        for (s, v) in src_data:
            if s == dst:
                v.append(symbol)
                return
        src_data.append((dst, [symbol]))

    def is_closed(self):
        """
        _check if the observation table is closed.
        Args:
            None
        Returns:
            tuple (bool, str): True if the observation table is closed and false otherwise.
                               If the table is not closed the escaping string is returned.
        """
        old_training_data = self.training_data
        self.training_data = {x: [] for x in self.sm_vector}
        for t in self.smi_vector:
            src_state = t[:-1]
            symbol = t[-1:]
            found = False
            for dst_state in self.sm_vector:
                if self.observation_table[dst_state] == self.observation_table[t]:
                    self._add_training_data(src_state, dst_state, symbol)
                    found = True
                    break
            if not found:
                return False, t

        assert self.training_data != old_training_data, \
            "No update happened from previous round. The algo will loop infinetely"
        return True, None

    def __getitem__(self, key):
        """
        Return an entry from the observation table

        @type key: tuple (str,str)
        @param key: A tuple specifying the row and column of the table
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
            value (str):
        Returns:
            None
        """
        row, col = key
        if row not in self.observation_table:
            self.observation_table[row] = {}
        self.observation_table[row][col] = value


class SFALearner(object):
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

    def __init__(
            self,
            alphabet,
            sink_size=3,
            loglevel=logging.INFO,
            logfile='angluin_sfa.log'):
        """
        Args:
            alphabet (list): input alphabet.
            sink_size (int): Maximum number of sink transitions.
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
        self.sink_size = sink_size

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
        state = mma.states[0]
        s_index = 0
        for i in range(index):
            for arc in state:
                if arc.guard.is_sat(w_string[i]):
                    state = mma.states[arc.dst_state]
                    s_index = arc.dst_state

        # The id of the state is its index inside the Sm list
        access_string = self.observation_table.sm_vector[s_index]
        logging.debug(
            'Access string for %d: %s - %d ',
            index,
            access_string,
            s_index)
        return access_string

    def _process_counter_example(self, mma, w_string):
        """"
        Process a counterexample in the Rivest-Schapire way.
        Args:
            mma (DFA): The hypothesis automaton
            w_string (str): The examined string to be consumed
        Return:
            None
        """
        if len(w_string) == 1:
            self.observation_table.smi_vector.append(w_string)
            for exp in self.observation_table.em_vector:
                self._fill_table_entry(w_string, exp)

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

        # First check if the transition is part of our training data.
        access_string = self._run_in_hypothesis(mma, w_string, diff - 1)
        wrong_transition = access_string + w_string[diff - 1]
        if wrong_transition not in self.observation_table.smi_vector:
            # If transition is not part of our training data add s_ib to Smi and
            # return to checking table closedness.
            self.observation_table.smi_vector.append(wrong_transition)
            for exp in self.observation_table.em_vector:
                self._fill_table_entry(wrong_transition, exp)
            return

        # This point presents a tradeoff between equivalence and membership
        # queries. If the transition in the counterexample'input_string breakpoint is not
        # part of our current training data (i.e. s_ib is not part of our Smi
        # set), then we assume a wrong transition and return to checking table
        # closure by adding s_ib to our training data. This saves a number of
        # membership queries since we don't add a row in our table unless
        # absolutely necessary. Notice that even if Equivalence queries are
        # expensive in general caching the result will be able to discover that
        # this iteration required a new state in the next equivalence query.

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
        i = random.choice(self.alphabet)
        self.observation_table.smi_vector.append(access_string + i)
        for e in self.observation_table.em_vector:
            self._fill_table_entry(access_string + i, e)

    #################### Hypothesis generation ######################

    def _get_predicate_guards(self, state, state_training_data):
        """
        Args:
            state (DFA state): The dfa state
            state_training_data (list): The training data set
        Returns:
            list: A list of transitions
        """
        # choose the sink transition.

        # First option: Just the maximum transition
        # sink = max(state_training_data, key=lambda x: len(x[1]))[0]

        # Second option: Heuristics based on RE filters properties
        max_size_trans = max(state_training_data, key=lambda x: len(x[1]))
        max_size_trans_l = [x for x in state_training_data if
                            len(x[1]) == len(max_size_trans[1])]

        target_states = [t[0] for t in max_size_trans_l]
        if len(max_size_trans_l) == 1:
            sink = max_size_trans[0]
        elif '' in target_states:
            sink = ''
        elif state in target_states:
            sink = state
        else:
            sink = random.choice(target_states)
        # End of sink selection

        transitions = []
        known_symbols = []
        for (t, data) in state_training_data:
            if t == sink:
                continue
            pred = SetPredicate(data)
            transitions.append((t, pred))
            known_symbols += data
        transitions.append(
            (sink, SetPredicate(set(self.alphabet) - set(known_symbols))))
        return transitions

    def get_sfa_conjecture(self):
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
        sfa = SFA(self.alphabet)
        for s in self.observation_table.sm_vector:
            transitions = self._get_predicate_guards(
                s, self.observation_table.training_data[s])
            for (t, pred) in transitions:
                src_id = self.observation_table.sm_vector.index(s)
                dst_id = self.observation_table.sm_vector.index(t)
                assert isinstance(
                    pred, SetPredicate), "Invalid type for predicate {}".format(pred)
                sfa.add_arc(src_id, dst_id, pred)

        # Mark the final states in the hypothesis automaton.
        i = 0
        for s in self.observation_table.sm_vector:
            sfa.states[i].final = self.observation_table[s, self.epsilon]
            i += 1
        return sfa

    ################## End of Hypothesis generation ####################

    def _init_table(self):
        """
        Initialize the observation table.
        """
        self.observation_table.sm_vector.append(self.epsilon)
        self.observation_table.smi_vector = [random.choice(self.alphabet)]
        self.observation_table.em_vector.append(self.epsilon)

        self._fill_table_entry(self.epsilon, self.epsilon)
        for s in self.observation_table.smi_vector:
            self._fill_table_entry(s, self.epsilon)

    def _init_table_from_dfa(self, mma):
        """
        Initializes table form a DFA
        Args:
            mma: The input automaton
        Returns:
            None
        """
        observation_table_init = ObservationTableInit(self.epsilon, self.alphabet)
        sm_vector, smi_vector, em_vector = observation_table_init.initialize(mma, True)
        self.observation_table.sm_vector = sm_vector
        self.observation_table.smi_vector = smi_vector
        self.observation_table.em_vector = em_vector

        logging.info('Initialized from DFA em_vector table is the following:')
        logging.info(em_vector)

        self._fill_table_entry(self.epsilon, self.epsilon)

        # list(set([])) is used to remove duplicates, [1:0] to remove epsilon
        for row in sorted(list(set(sm_vector + smi_vector)), key=len)[1:]:
            for column in em_vector:
                self._fill_table_entry(str(row), str(column))

    def learn_sfa(self, mma=None):
        """
        Implements the high level loop of the algorithm for learning a
        Mealy machine.
        Args:
            mma:
        Returns:
            MealyMachine: A model for the Mealy machine to be learned.
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
                closed, s = self.observation_table.is_closed()
                if not closed:
                    logging.debug('Closing table.')
                    self._ot_make_closed(s)
                else:
                    logging.debug('Table closed.')

            # Create conjecture
            sfa = self.get_sfa_conjecture()

            logging.info('Generated conjecture machine with %d states.',
                         len(list(sfa.states)))

            # _check correctness
            logging.debug('Running equivalence query.')
            found, counter_example = self._equivalence_query(sfa)

            # Are we done?
            if found:
                logging.info('No counterexample found. Hypothesis is correct!')
                break

            # Add the new experiments into the table to reiterate the
            # learning loop
            logging.info(
                'Processing counterexample %s with length %d.',
                counter_example,
                len(counter_example))
            self._process_counter_example(sfa, counter_example)

        logging.info('Learning complete.')
        return '', sfa


if __name__ == '__main__':
    print 'Angluin Algorithm for learning Symbolic Automata abstract \
class implementation.'
