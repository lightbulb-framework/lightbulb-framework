from lightbulb.core.utils.browserhandler import BrowserHandler
import os.path

META = {
        'author': 'George Argyros, Ioannis Stais',
        'description': 'Learns a Browser parser using a file containing regular expressions or grammar as input',
        'type':'GOFA',
        'options': [
            ('WSPORT', "8000", True, 'The Web Socket server port'),
            ('WBPORT', "8080", True, 'The Web server port'),
            ('HOST', "localhost", True, 'The Web server and web socket host'),
            ('INPUT', True, True, 'Preload the input filter'),
            ('DELAY', "50", True, 'Wait time for objects to load'),
        ],
        'comments': ['Sample comment 1', 'Sample comment 2']
    }

class Handler(BrowserHandler):
    def setup(self, configuration):
        self.wsport = configuration['WSPORT']
        self.wbport = configuration['WBPORT']
        self.browserparse = True
        self.delay = configuration['DELAY']
        self.host = configuration['HOST']


class Module():


    def __init__(self, configuration):
        self.configuration = configuration
        self.result = ""
        self.browser_socket_handler = Handler(configuration)

    def check_payload(self, test):
        from curses.ascii import isprint

        if os.path.isfile(test):
            with open(test, "r") as ins:
                for line in ins:
                    result = self.browser_socket_handler.query(''.join([x for x in line if isprint(x)]))
                    if result:
                        self.result = self.result+"\n"+line
        elif os.path.exists(self.configuration['INPUT']):
            for name in os.listdir(self.configuration['INPUT']):
                self.check_payload(self.configuration['INPUT'] +"/"+name)
        else:
            self.result = self.browser_socket_handler.query(self.configuration['INPUT'])
        pass

    def learn(self):
        self.check_payload(self.configuration['INPUT'])
        pass


    def stats(self):
        return [("Membership Queries","")]


    def getresult(self):
        return "Result", self.result