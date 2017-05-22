import sys
from lightbulb.core.utils.ipc import Pipe
import base64
from lightbulb.core.utils.webserverhandler import WebServerHandler
from lightbulb.core.utils.SimpleWebServer import SimpleWebServer
from lightbulb.core.utils.SimpleWebSocketServer import SimpleWebSocketServer
from lightbulb.core.utils.sockethandler import SocketHandler
from lightbulb.core.utils.common import accept_bool
from threading import Thread

META = {
    'author': 'George Argyros, Ioannis Stais',
    'name': 'BrowserHandler',
    'description': 'Performs membership queries in a browser',
    'type': 'UTIL',
    'options': [
        ('WSPORT', "8000", True, 'The Web Socket server port'),
        ('WBPORT', "8080", True, 'The Web server port'),
        ('BROWSERPARSE', True, True, 'Positive response if browser parses a JavaScript payload'),
        ('DELAY', "50", True, 'Wait time for objects to load'),
        ('HOST', "localhost", True, 'The Web server and web socket host'),
        ('ECHO', None, False, 'Optional custom debugging message that is printed on each membership request'),
    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}


def serve(server):
    """
    Initializes the websocket server
    Args:
        server (SimpleWebSocketServer): The web socket server
    Returns:
        None
    """
    server.serveforever()

def serve_html(server):
    """
    Initializes the web browser server
    Args:
        server (SimpleWebServer): The web browser server
    Returns:
        None
    """
    server.serveforever()


class BrowserHandler:
    def __init__(self, configuration):
        """
        Initialization function
        Args:
            wsport (int):     The web server port
            wbport (int):     The web socket server port
            browserparses (bool):   If set to true, then query is true
                                    if browser parses JavaScript.
                                    If set to false, then query is true
                                    if browser does not parse JavaScript.
        """

        self.setup(configuration)
        self.echo = None
        if "ECHO" in configuration:
            self.echo = configuration['ECHO']
        self.wsport = int(self.wsport)
        self.wbport = int(self.wbport)
        self.browserparse = accept_bool(self.browserparse)
        self.websocket = None
        self.webbrowser = None
        self.websocketserver = None
        self.webbrowserserver = None

        if self.browserparse:
            # Learn what the browser parses as valid javascript
            self.return_code_1 = '0'
            self.return_code_2 = '1'
        else:
            # Learn what the browser does not parse as valid javascript
            self.return_code_1 = '1'
            self.return_code_2 = '0'

        parent_conn_a, child_conn_a = Pipe()
        websocketserver = SimpleWebSocketServer(
            self.host, self.wsport, SocketHandler, parent_conn_a, child_conn_a, self.wsport)
        print 'Starting WebSocket Server at port ' + repr(self.wsport) + ': ',
        websocket = Thread(
            target=serve,
            args=(
                websocketserver,
            ))
        websocket.setDaemon(True)
        websocket.start()
        print 'OK'
        print 'Starting HTTP Server at port ' + repr(self.wbport) + ': ',
        webbrowserserver = SimpleWebServer(self.host, self.wbport, WebServerHandler, self.delay, self.wsport)
        webbrowser = Thread(
            target=serve_html,
            args=(
                webbrowserserver,
            ))
        webbrowser.setDaemon(True)
        webbrowser.start()
        print 'OK'
        print 'Please connect your Browser at http://' + self.host + ':' + repr(self.wbport)
        print 'Verifying Web Socket connection:',
        updates = parent_conn_a.recv()
        if updates[0] == "browserstatus" and updates[1] == 1:
            print 'OK'
        else:
            print 'FAIL'
        print 'Awaiting initialization command:',
        updates = parent_conn_a.recv()
        if updates[0] == "browserresponse" and updates[1] == "INIT":
            print 'OK'
        else:
            print 'FAIL'
        self.server = (parent_conn_a, child_conn_a)

        self.websocket = websocket
        self.webbrowser = webbrowser
        self.websocketserver = websocketserver
        self.webbrowserserver = webbrowserserver

    def setup(self, configuration):
        self.wsport = configuration['WSPORT']
        self.wbport = configuration['WBPORT']
        self.browserparse = configuration['BROWSERPARSE']
        self.delay = configuration['DELAY']
        self.host = configuration['HOST']

    def query(self, string):

        self.server[0].send(["serverrequest", ''.join(x.encode('hex') for x in string)])
        updates = self.server[0].recv()
        if self.echo:
            print self.echo
        if updates[0] == "browserresponse" \
                and updates[1] == self.return_code_1:
            return True
        if updates[0] == "browserresponse" \
                and updates[1] == self.return_code_2:
            return False
        if updates[0] == "browserstatus" and updates[1] == 0:
            print 'Browser disconnected. Awaiting to connect again..'
            while True:
                print 'Verifying Web Socket connection:',
                updates = self.server[0].recv()
                if updates[0] == "browserstatus" and updates[1] == 1:
                    print 'OK'
                else:
                    print 'FAIL'
                print 'Awaiting initialization command:',
                updates = self.server[0].recv()
                if updates[0] == "browserresponse" and updates[1] == "INIT":
                    print 'OK'
                else:
                    print 'FAIL'
                return self.query(string)

    def __del__(self):
        print 'del'
        if self.websocketserver is not None:
            self.websocketserver.close()
        if self.webbrowserserver is not None:
            self.webbrowserserver.close()

