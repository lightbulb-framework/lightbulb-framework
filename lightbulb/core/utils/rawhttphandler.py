import re
import urllib
import sys
import socket
import ssl

META = {
    'author': 'George Argyros, Ioannis Stais',
    'name': 'RawHTTPHandler',
    'description': 'Performs membership queries in a browser filter',
    'type': 'UTIL',
    'options': [
        ('MESSAGE', "GET / HTTP/1.1", True, 'The HTTP raw request to send. The targetted parameter must me marked as  --LIGHTBULB--REPLACE--HERE--'),
        ('HOST', "127.0.0.1", True, 'The target host'),
        ('PORT', 80, True, 'The target port'),
        ('HTTPS', False, True, 'Whether to use SSL/TLS'),
        ('BLOCK', None, False, 'The response string that indicates that the WAF blocks the request'),
        ('BYPASS', None, False, 'The response string that indicates that the WAF allows the request'),

    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}


class RawHTTPHandler:

    def __init__(self, configuration):
        self.setup(configuration)
        socket.setdefaulttimeout = 0.50

    def setup(self, configuration):
        self.message = configuration['MESSAGE']
        self.host = configuration['HOST']
        self.port = configuration['PORT']
        self.https = configuration['HTTPS']
        self.fail_regex = configuration['BLOCK']
        self.success_regex = configuration['BYPASS']

    def query(self, string, verbose = False):
        """
        Perform a query
        Args:
           query (str): The SQL query
        Returns:
            bool: A success or failure response
        """
        if string:
            request = self.message.replace(
                "--LIGHTBULB--REPLACE--HERE--",
                urllib.quote_plus(string))
        else:
            request = self.message

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.settimeout(0.30)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setblocking(1)
            if self.https > -1:
                wrappedSocket = ssl.wrap_socket(s)
                s = wrappedSocket
            s.connect((self.host, self.port))

            s.send(request)
            response = (s.recv(1000000))
            s.shutdown(1)
            s.close()
            s = None
        except:
            print 'error when making the request'
            print sys.exc_info()
            response = self.fail_regex

        try:
            found = False
            html = response.decode('utf-8')
            print html
            if self.fail_regex is not None and self.fail_regex != "":
                pattern = r'' + self.fail_regex
                hits = re.findall(pattern, html)
                if len(hits) > 0:
                    found = True
                else:
                    found = False
            if not found:
                if self.success_regex is not None and self.success_regex != "":
                    pattern = r'' + self.success_regex
                    hits = re.findall(pattern, html)
                    if len(hits) > 0:
                        found = False
                    else:
                        found = True
            if verbose:
                return found, request, response
            else:
                return found
        except:
            print 'error when decoding'
            print sys.exc_info()
            return True

        print 'Please give either a BLOCK or a BYPASS pattern'
        exit(1)
