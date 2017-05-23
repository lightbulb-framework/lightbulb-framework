from lightbulb.core.utils.common import findlibrary
from lightbulb.modules.gen_waf_tree import Module as GenerateModule
from lightbulb.core.modules.sfadiff import SFADiff
from lightbulb.core.operate import operate_diff
import random
import time
from lightbulb.core.base import options_as_dictionary

class GenerateTree(GenerateModule):
    def __init__(self, configuration):
        self.configuration = configuration
        self.distinguisher = None
        self.name = None
        self.queries = 0
        self.membership_queries = 0
        self.cache_membership_queries = 0
        self.equivalence_queries = 0
        self.cache_equivalence_queries = 0
        self.equivalence_queries_cached_membership = 0
        self.browserstates = 0
        self.cross_check_times = 0
        self.wafs = configuration['WAFS']
        self.seed_files_list = configuration['SEED_FILES_LIST']

    def get_waf_rules(self, waf_key_a, waf_key_b, rules_a_already_used, rules_b_already_used):
        """
        Args:
            waf_key_a (str): The WAF name
            waf_key_b (str): The WAF name
            rules_a_already_used (list): A list containing the names of the files
                                that will be excluded
            rules_b_already_used (list): A list containing the names of the files
                                that will be excluded
        Returns:
            str,str: Two file paths, which are the selected rulesets
        """
        available_files_a = [x for x in self.seed_files_list if x not in rules_a_already_used]
        available_files_b = [x for x in self.seed_files_list if x not in rules_b_already_used]
        if self.configuration['RANDOM']:
            random.shuffle(available_files_a) 
            random.shuffle(available_files_b)
        selected_rule_a = findlibrary(available_files_a[0])
        selected_rule_b = findlibrary(available_files_b[0])
        print ' * Rules ' + selected_rule_a, " and " + selected_rule_b + " where selected in this test"
        return selected_rule_a, selected_rule_b


    
    def examine_sets(self, waf_set, diff):
        """
        This function uses a distinguish string and separates the
        provided WAFs into two lists, depending on if they accept
        or reject the string.
        Args:
            waf_set (list): A list of WAF names
            diff (str): A given candidate distinguish string.
        Returns:
            list,list: Two WAFs lists,depending on if they accept
                        or reject the string.
        """
        part_a = []
        part_b = []
        for waf in waf_set:
            httphandler = self.wafs[waf]['HANDLER']
            if not httphandler.query(diff):
                part_a.append(waf)
            else:
                part_b.append(waf)
        return part_a, part_b

    def sfadiff(self, wafkeyA, wafkeyB, ruleA, ruleB):
        """
        This function finds a distinguish string between two WAFs,
        by performing sfadiff algorithm. The rulesets do not need to
        be precise.
        Args:
            waf_key_a (str): The first WAF name
            waf_key_b (str): The SECOND WAF name
            selected_rule_a (str): The path for the file containing the known
                         rules of the first WAF
            selected_rule_b (str): The path for the file containing the known
                         rules of the SECOND WAF
        Returns:
            str: A distinguish string
        """

        configuration = {
            'ALPHABET':  self.configuration['ALPHABET'],
            'SEED_FILE_A' : ruleA,
            'SEED_FILE_TYPE_A' : 'FLEX',
            'TESTS_FILE_A': None,
            'TESTS_FILE_TYPE_A': 'FLEX',
            'SEED_FILE_B' :  ruleB,
            'SEED_FILE_TYPE_B' :  'FLEX',
            'TESTS_FILE_B': None,
            'TESTS_FILE_TYPE_B': 'FLEX',
            'DFA1_MINUS_DFA2': False,
            'HANDLER_A': self.wafs[wafkeyA]['HANDLER'],
            'HANDLER_B': self.wafs[wafkeyB]['HANDLER']
        }

        class Module_A(SFADiff):
            def setup(self, configuration):
                self.alphabet = configuration['ALPHABET']
                self.seed_file = configuration['SEED_FILE_A']
                self.seed_file_type = configuration['SEED_FILE_TYPE_A']
                self.tests_file = configuration['TESTS_FILE_A']
                self.tests_file_type = configuration['TESTS_FILE_TYPE_A']
                self.dfa1_minus_dfa2 = False
                self.handler = configuration['HANDLER_A']

        class Module_B(SFADiff):
            def setup(self, configuration):
                self.alphabet = configuration['ALPHABET']
                self.seed_file = configuration['SEED_FILE_B']
                self.seed_file_type = configuration['SEED_FILE_TYPE_B']
                self.tests_file = configuration['TESTS_FILE_B']
                self.tests_file_type = configuration['TESTS_FILE_TYPE_B']
                self.dfa1_minus_dfa2 = False
                self.handler = configuration['HANDLER_B']


        dist_start_time = time.time()
        res = options_as_dictionary(operate_diff(Module_A, configuration, Module_B, configuration))
        print res
        print("Printing Execution Time: %s" % (time.time() - dist_start_time))
        self.membership_queries = self.membership_queries + int(res['Target A Membership Queries']) + int(res['Target B Membership Queries'])
        self.cache_membership_queries = self.cache_membership_queries + int(res['Target A Cached Membership Queries']) + int(res['Target B Cached Membership Queries'])
        self.equivalence_queries = self.equivalence_queries + int(res['Target A Equivalence Queries']) + int(res['Target B Equivalence Queries'])
        self.cache_equivalence_queries = self.cache_equivalence_queries + int(res['Target A Cached Equivalence Queries']) + int(res['Target B Cached Equivalence Queries'])
        self.equivalence_queries_cached_membership =  self.equivalence_queries_cached_membership + int(res['Target A Cached Membership Equivalence Queries']) + int(res['Target B Cached Membership Equivalence Queries'])
        self.browserstates = self.browserstates + int(res['Learned Target A model states']) + int(res['Learned Target B model states'])
        self.cross_check_times = self.cross_check_times + int(res['Cross-check times'])
        return res['Bypass']
