from lightbulb.core.utils.httphandler import HTTPHandler
from lightbulb.core.utils.common import findlibrary
import json

META = {
    'author': 'George Argyros, Ioannis Stais',
    'description': 'Identifies a WAF filter using a distinguish tree',
    'type':'Distinguisher',
    'options': [
        ('FILE', None, True, 'File containting a distinguish tree'),
        ('URL', "http://127.0.0.1", True, 'The target URL'),
        ('REQUEST_TYPE', "GET", True, 'The HTTP request type (GET/POST)'),
        ('PARAM', "input", True, 'The request parameter'),
        ('BLOCK', None, False, 'The response string that indicates that the WAF blocks the request'),
        ('BYPASS', None, False, 'The response string that indicates that the WAF allows the request'),
        ('PROXY_SCHEME', None, False, 'The proxy scheme (e.g. http, https'),
        ('PROXY_HOST', None, False, 'The proxy host'),
        ('PROXY_PORT', None, False, 'The proxy port'),
        ('PROXY_USERNAME', None, False, 'The proxy username'),
        ('PROXY_PASSWORD', None, False, 'The proxy password'),
        ('USER_AGENT', "Mozilla/5.0", True, 'The request user agent'),
        ('REFERER', "http://google.com", True, 'The request referrer'),
        ('PRELOAD', False, True, 'Preload the input filter'),
    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}

class Handler(HTTPHandler):
    def setup(self, configuration):
        self.url = configuration['URL']
        self.request_type = configuration['REQUEST_TYPE']
        self.param = configuration['PARAM']
        self.block = configuration['BLOCK']
        self.bypass = configuration['BYPASS']
        self.proxy_scheme = configuration['PROXY_SCHEME']
        self.proxy_host = configuration['PROXY_HOST']
        self.proxy_port = configuration['PROXY_PORT']
        self.proxy_username = configuration['PROXY_USERNAME']
        self.proxy_password = configuration['PROXY_PASSWORD']
        self.user_agent = configuration['USER_AGENT']
        self.referer = configuration['REFERER']


class Module():


    def __init__(self, configuration):
        self.distinguisher = None
        self.loadfile(findlibrary(configuration['FILE']))
        self.httphandler = Handler(configuration)
        self.name = None
        self.queries = 0

    def loadfile(self, input_filename):
        """Loads a distinguish tree from a custom location"""
        with open(input_filename, 'r') as input_file:
            self.distinguisher = json.load(input_file)

    def algorithm(self, check):
        """
        This function distinguish a WAF using
        the current distinguish tree and a function
        that performs membership queries
        Args:
            check (func): The membership query function
        Returns:
            str: The identified WAF name
        """
        pos = self.distinguisher
        while True:
            pos = pos["RESULT"][str(check(pos["STRING"]))]
            if not isinstance(pos, dict):
                return pos


    def learn(self):
        def check(string):
            """
            This function performs a membership query
            Args:
                  string (str): The examined string
            Returns:
                  str: A string with values either 'true' or 'false'
            """
            self.queries = self.queries + 1
            return self.httphandler.query(string)

        self.name = self.algorithm(check)


    def stats(self):
        return  [("Membership Queries",self.queries)]


    def getresult(self):
        return  "Waf", self.name