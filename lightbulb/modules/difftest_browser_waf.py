from lightbulb.core.utils.browserhandler import BrowserHandler
from lightbulb.core.utils.httphandler import HTTPHandler
import os.path

META = {
        'author': 'George Argyros, Ioannis Stais',
        'description': 'Generates a large number of mutations in an input string and tests browser and WAF',
        'type':'GOFA',
        'options': [
            ('INPUT', True, True, 'Preload the input filter'),
            ('WSPORT', "8000", True, 'The Web Socket server port'),
            ('WBPORT', "8080", True, 'The Web server port'),
            ('HOST', "localhost", True, 'The Web server and web socket host'),
            ('DELAY', "50", True, 'Wait time for objects to load'),
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
        ],
        'comments': ['Sample comment 1', 'Sample comment 2']
    }

class Handler_A(BrowserHandler):
    def setup(self, configuration):
        self.wsport = configuration['WSPORT']
        self.wbport = configuration['WBPORT']
        self.browserparse = True
        self.delay = configuration['DELAY']
        self.host = configuration['HOST']

class Handler_B(HTTPHandler):
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
        self.configuration = configuration
        self.result = ""
        self.browser_socket_handler = Handler_A(configuration['WSPORT'])
        self.httphandler = Handler_B(configuration)

    def check_payload(self, test):
        from curses.ascii import isprint

        if os.path.isfile(test):
            with open(test, "r") as ins:
                for line in ins:
                    mystr = ''.join([x for x in line if isprint(x)])
                    if not self.httphandler.query(mystr):
                        if self.browser_socket_handler.query(mystr):
                            self.result = self.result+"\n"+line
        elif os.path.exists(self.configuration['INPUT']):
            for name in os.listdir(self.configuration['INPUT']):
                self.check_payload(self.configuration['INPUT'] +"/"+name)
        else:
            self.result = self.httphandler.query(self.configuration['INPUT']) and self.browser_socket_handler.query(self.configuration['INPUT'])
        pass

    def learn(self):
        self.check_payload(self.configuration['INPUT'])
        pass


    def stats(self):
        return [("Membership Queries","")]


    def getresult(self):
        return "Result", self.result