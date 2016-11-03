from lightbulb.core.base import options_as_dictionary
from collections import OrderedDict
from lightbulb.core.operate import manage
from lightbulb.core.utils.common import findlibrary
import json


META = {
    'author': 'George Argyros, Ioannis Stais',
    'description': 'Verifies a distinguish tree for a list of WAF filters',
    'type':'Distinguisher',
    'options': [
        ('WAFCONF', None, True, 'File containting the WAFs configuration'),
        ('FILE', None, True, 'The generated distinguish string'),
        ('PROXY_SCHEME', None, False, 'The proxy scheme (e.g. http, https'),
        ('PROXY_HOST', None, False, 'The proxy host'),
        ('PROXY_PORT', None, False, 'The proxy port'),
        ('PROXY_USERNAME', None, False, 'The proxy username'),
        ('PROXY_PASSWORD', None, False, 'The proxy password'),
        ('USER_AGENT', "Mozilla/5.0", True, 'The request user agent'),
        ('REFERER', "http://google.com", True, 'The request referrer'),
    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}




class Module():


    def __init__(self, configuration):
        self.configuration = configuration
        self.stats_records = []
        with open(findlibrary(configuration['WAFCONF']), 'r') as fp:
            self.wafs = json.load(fp,object_pairs_hook=OrderedDict)
        self.name = "CORRECT"


    def learn(self):
        for waf in self.wafs:
            configuration = {
                'FILE' : self.configuration['FILE'],
                'URL' : self.wafs[waf]['data']['URL'],
                'REQUEST_TYPE' : self.wafs[waf]['data']['REQUEST_TYPE'],
                'PARAM' : self.wafs[waf]['data']['PARAM'],
                'BLOCK' : self.wafs[waf]['data']['BLOCK'],
                'BYPASS' : self.wafs[waf]['data']['BYPASS'],
                'PROXY_SCHEME' : self.configuration['PROXY_SCHEME'],
                'PROXY_HOST' : self.configuration['PROXY_HOST'],
                'PROXY_PORT' : self.configuration['PROXY_PORT'],
                'PROXY_USERNAME' : self.configuration['PROXY_USERNAME'],
                'PROXY_PASSWORD' : self.configuration['PROXY_PASSWORD'],
                'USER_AGENT' : self.configuration['USER_AGENT'],
                'ALPHABET': None,
                'REFERER' : self.configuration['REFERER'],
            }
            res = options_as_dictionary(manage("distinguish_waf", configuration))
            if res['Waf'] == self.wafs[waf]['name']:
                self.stats_records.append((self.wafs[waf]['name'],'OK'))
            else:
                self.stats_records.append((self.wafs[waf]['name'], 'FAIL'))
                self.name = "INCORRECT"


    def getresult(self):
        return  "Status", self.name

    def stats(self):
        return  self.stats_records


