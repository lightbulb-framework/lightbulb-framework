from lightbulb.core.base import options_as_dictionary
from lightbulb.core.utils.httphandler import HTTPHandler
from lightbulb.core.utils.common import findlibrary
from collections import OrderedDict
from lightbulb.core.modules.sfadiff import SFADiff
from symautomata.alphabet import createalphabet
from lightbulb.core.operate import operate_diff
import json
import os
import random
import time

META = {
    'author': 'George Argyros, Ioannis Stais',
    'description': 'Generates a distinguish tree for a list of WAF filters',
    'type':'Distinguisher',
    'options': [
        ('FILE_IN', None, True, 'File containting the WAFs configuration'),
        ('FILE_OUT', None, True, 'The generated distinguish string'),
        ('RANDOM', False, True, 'Use a random rule from the IDS folders'),
        ('PROXY_SCHEME', None, False, 'The proxy scheme (e.g. http, https'),
        ('PROXY_HOST', None, False, 'The proxy host'),
        ('PROXY_PORT', None, False, 'The proxy port'),
        ('PROXY_USERNAME', None, False, 'The proxy username'),
        ('PROXY_PASSWORD', None, False, 'The proxy password'),
        ('USER_AGENT', "Mozilla/5.0", True, 'The request user agent'),
        ('REFERER', "http://google.com", True, 'The request referrer'),
        ('ALPHABET', None, False, 'File containing the alphabet'),
        ('CLASSIC', False, True, 'Use classic equivalence if sfadiff finds no counterexample'),
    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}



class Module():


    def __init__(self, configuration):
        self.configuration = configuration
        self.distinguisher = None
        self.name = None
        self.queries = 0
        with open(findlibrary(configuration['FILE_IN']), 'r') as fp:
            self.wafs = json.load(fp,object_pairs_hook=OrderedDict)
        self.membership_queries = 0
        self.cache_membership_queries = 0
        self.equivalence_queries = 0
        self.cache_equivalence_queries = 0
        self.equivalence_queries_cached_membership = 0
        self.browserstates = 0
        self.cross_check_times = 0

    def get_files_by_file_size(self, dirname, rules_already_used, reverse=False):
        """
        Return list of file paths in directory sorted by file size
        Args:
            dirname (str): The target directory name
            rules_already_used (list): A list containing the names of the files
                                that will be excluded
            reverse (bool): Defines the order
        Returns:
            list: A list of file paths
        """
        # Get list of files
        filepaths = []
        for basename in os.listdir(dirname):
            filename = os.path.join(dirname, basename)
            if os.path.isfile(filename) and filename not in rules_already_used and not filename.endswith(".py") and not filename.endswith(".pyc"):
                filepaths.append(filename)

        # Re-populate list with filename, size tuples
        for i in xrange(len(filepaths)):
            filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))

        # Sort list by file size
        # If reverse=True sort from largest to smallest
        # If reverse=False sort from smallest to largest
        filepaths.sort(key=lambda filename: filename[1], reverse=reverse)

        # Re-populate list with just filenames
        for i in xrange(len(filepaths)):
            filepaths[i] = filepaths[i][0]
        return filepaths

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
        waf_a_rules_folder = findlibrary(self.wafs[waf_key_a]["data"]["RULE"])
        waf_b_rules_folder = findlibrary(self.wafs[waf_key_b]["data"]["RULE"])
        if os.path.isfile(waf_a_rules_folder):
            selected_rule_a = waf_a_rules_folder
        else:
            ruleslist = self.get_files_by_file_size(waf_a_rules_folder, rules_a_already_used)
            if self.configuration['RANDOM']:
                random.shuffle(ruleslist)
            if len(ruleslist) == 0:
                selected_rule_a = ''
            else:
                selected_rule_a = ruleslist[0]
        if os.path.isfile(waf_b_rules_folder):
            selected_rule_b = waf_b_rules_folder
        else:
            ruleslist = self.get_files_by_file_size(waf_b_rules_folder, rules_b_already_used)
            if self.configuration['RANDOM']:
                random.shuffle(ruleslist)
            if len(ruleslist) == 0:
                selected_rule_b = ''
            else:
                selected_rule_b = ruleslist[0]
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
            configure = {
                            'URL': self.wafs[waf]["data"]["URL"],
                            'REQUEST_TYPE': self.wafs[waf]["data"]["REQUEST_TYPE"],
                            'PARAM': self.wafs[waf]["data"]["PARAM"],
                            'BLOCK': self.wafs[waf]["data"]["BLOCK"],
                            'BYPASS': self.wafs[waf]["data"]["BYPASS"],
                            'PROXY_SCHEME': self.configuration['PROXY_SCHEME'],
                            'PROXY_HOST': self.configuration['PROXY_HOST'],
                            'PROXY_PORT': self.configuration['PROXY_PORT'],
                            'PROXY_USERNAME': self.configuration['PROXY_USERNAME'],
                            'PROXY_PASSWORD': self.configuration['PROXY_PASSWORD'],
                            'USER_AGENT': self.configuration['USER_AGENT'],
                            'REFERER': self.configuration['REFERER']
            }
            httphandler = HTTPHandler(configure)
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
        'SEED_FILE_A' : ruleA,
        'SEED_FILE_TYPE_A' : 'FLEX',
        'TESTS_FILE_A': None,
        'TESTS_FILE_TYPE_A': 'FLEX',
        'URL_A' : self.wafs[wafkeyA]["data"]["URL"],
        'REQUEST_TYPE_A' : self.wafs[wafkeyA]["data"]["REQUEST_TYPE"],
        'PARAM_A' : self.wafs[wafkeyA]["data"]["PARAM"],
        'BLOCK_A' : self.wafs[wafkeyA]["data"]["BLOCK"],
        'BYPASS_A' : self.wafs[wafkeyA]["data"]["BYPASS"],
        'SEED_FILE_B' :  ruleB,
        'SEED_FILE_TYPE_B' :  'FLEX',
        'TESTS_FILE_B': None,
        'TESTS_FILE_TYPE_B': 'FLEX',
        'URL_B' :  self.wafs[wafkeyB]["data"]["URL"],
        'REQUEST_TYPE_B' :  self.wafs[wafkeyB]["data"]["REQUEST_TYPE"],
        'PARAM_B' :  self.wafs[wafkeyB]["data"]["PARAM"],
        'BLOCK_B' :  self.wafs[wafkeyB]["data"]["BLOCK"],
        'BYPASS_B' :  self.wafs[wafkeyB]["data"]["BYPASS"],
        'PROXY_SCHEME' : self.configuration['PROXY_SCHEME'],
        'PROXY_HOST' : self.configuration['PROXY_HOST'],
        'PROXY_PORT' : self.configuration['PROXY_PORT'],
        'PROXY_USERNAME' : self.configuration['PROXY_USERNAME'],
        'PROXY_PASSWORD' : self.configuration['PROXY_PASSWORD'],
        'USER_AGENT' : self.configuration['USER_AGENT'],
        'REFERER' : self.configuration['REFERER'],
        'ALPHABET': self.configuration['ALPHABET'],
        }

        class Handler_A(HTTPHandler):
            def setup(self, configuration):
                self.url = configuration['URL_A']
                self.request_type = configuration['REQUEST_TYPE_A']
                self.param = configuration['PARAM_A']
                self.block = configuration['BLOCK_A']
                self.bypass = configuration['BYPASS_A']
                self.proxy_scheme = configuration['PROXY_SCHEME']
                self.proxy_host = configuration['PROXY_HOST']
                self.proxy_port = configuration['PROXY_PORT']
                self.proxy_username = configuration['PROXY_USERNAME']
                self.proxy_password = configuration['PROXY_PASSWORD']
                self.user_agent = configuration['USER_AGENT']
                self.referer = configuration['REFERER']

        class Module_A(SFADiff):
            def setup(self, configuration):
                self.alphabet = createalphabet(configuration['ALPHABET'])
                self.seed_file = configuration['SEED_FILE_A']
                self.seed_file_type = configuration['SEED_FILE_TYPE_A']
                self.tests_file = configuration['TESTS_FILE_A']
                self.tests_file_type = configuration['TESTS_FILE_TYPE_A']
                self.dfa1_minus_dfa2 = False
                self.handler = Handler_A(configuration)

        class Handler_B(HTTPHandler):
            def setup(self, configuration):
                self.url = configuration['URL_B']
                self.request_type = configuration['REQUEST_TYPE_B']
                self.param = configuration['PARAM_B']
                self.block = configuration['BLOCK_B']
                self.bypass = configuration['BYPASS_B']
                self.proxy_scheme = configuration['PROXY_SCHEME']
                self.proxy_host = configuration['PROXY_HOST']
                self.proxy_port = configuration['PROXY_PORT']
                self.proxy_username = configuration['PROXY_USERNAME']
                self.proxy_password = configuration['PROXY_PASSWORD']
                self.user_agent = configuration['USER_AGENT']
                self.referer = configuration['REFERER']

        class Module_B(SFADiff):
            def setup(self, configuration):
                self.alphabet = createalphabet(configuration['ALPHABET'])
                self.seed_file = configuration['SEED_FILE_B']
                self.seed_file_type = configuration['SEED_FILE_TYPE_B']
                self.tests_file = configuration['TESTS_FILE_B']
                self.tests_file_type = configuration['TESTS_FILE_TYPE_B']
                self.dfa1_minus_dfa2 = False
                self.handler = Handler_B(configuration)

        dist_start_time = time.time()
        res = options_as_dictionary(operate_diff(Module_A, configuration, Module_B, configuration))
        print("Printing Execution Time: %s" % (time.time() - dist_start_time))
        self.membership_queries = self.membership_queries + int(res['Target A Membership Queries']) + int(res['Target B Membership Queries'])
        self.cache_membership_queries = self.cache_membership_queries + int(res['Target A Cached Membership Queries']) + int(res['Target B Cached Membership Queries'])
        self.equivalence_queries = self.equivalence_queries + int(res['Target A Equivalence Queries']) + int(res['Target B Equivalence Queries'])
        self.cache_equivalence_queries = self.cache_equivalence_queries + int(res['Target A Cached Equivalence Queries']) + int(res['Target B Cached Equivalence Queries'])
        self.equivalence_queries_cached_membership =  self.equivalence_queries_cached_membership + int(res['Target A Cached Membership Equivalence Queries']) + int(res['Target B Cached Membership Equivalence Queries'])
        self.browserstates = self.browserstates + int(res['Learned Target A model states']) + int(res['Learned Target B model states'])
        self.cross_check_times = self.cross_check_times + int(res['Cross-check times'])
        return res['Bypass']

    def generate_distinguish_tree(self, waf_set):
        """
        This function performs the selected algorithm for
        each provided WAF set, and at the generated
        subsets.
        Args:
            waf_set (list): A list of WAF names
        Returns:
            dict: A distinguish tree
        """
        print 'New Set was received for assesment:'
        print [self.wafs[x]['name'] for x in waf_set]
        if len(waf_set) > 1:
            waf_key_a = waf_set[0]
            waf_key_b = waf_set[1]
            diff = None
            rules_a_already_used = []
            rules_b_already_used = []
            while diff is None:
                selected_rule_a, selected_rule_b = self.get_waf_rules(
                    waf_key_a, waf_key_b, rules_a_already_used, rules_b_already_used)
                if selected_rule_a == '' and selected_rule_b == '':
                    print 'All rules where exhausted and it was not possible to find a difference'
                    exit(1)
                if selected_rule_a != '':
                    rules_a_already_used.append(selected_rule_a)
                if selected_rule_b != '':
                    rules_b_already_used.append(selected_rule_b)
                diff = self.sfadiff(waf_key_a, waf_key_b, selected_rule_a, selected_rule_b)
                if diff is None:
                    continue
            print 'Diff is: '+diff
            part_a, part_b = self.examine_sets(waf_set, diff)
            print 'The following parts were discovered:'
            print [self.wafs[x]['name'] for x in part_a], ' - ', [self.wafs[x]['name'] for x in part_b]
            return {
                "STRING": diff, "RESULT": {
                    'False': self.generate_distinguish_tree(part_a),
                    'True': self.generate_distinguish_tree(part_b)
                }
            }
        else:
            print 'Finalizing ' + self.wafs[waf_set[0]]["name"]
            return self.wafs[waf_set[0]]["name"]



    def learn(self):
        newdistinguisher = self.generate_distinguish_tree(list(self.wafs))
        with open(findlibrary(self.configuration['FILE_OUT']), 'w') as fp:
            json.dump(newdistinguisher, fp, sort_keys=True, indent=4)

    def stats(self):
        return [
            ('Membership Queries', repr(self.membership_queries)),
            ('Cached Membership Queries', repr(self.cache_membership_queries)),
            ('Equivalence Queries', repr(self.equivalence_queries)),
            ('Cached Equivalence Queries', repr(self.cache_equivalence_queries)),
            ('Cached Membership Equivalence Queries', repr(self.equivalence_queries_cached_membership)),
            ('Learned Total States', repr(self.browserstates)),
            ('Cross-check times', repr(self.cross_check_times))
        ]

    def getresult(self):
        return  "Tree Location", self.configuration['FILE_OUT']