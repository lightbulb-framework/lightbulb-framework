import re
import urllib
import urllib2
from urllib2 import Request


META = {
    'author': 'George Argyros, Ioannis Stais',
    'name':'HTTPHandler',
    'description': 'Performs membership queries in a browser filter',
    'type': 'UTIL',
    'options': [
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
        ('ECHO', None, False, 'Optional custom debugging message that is printed on each membership request'),
    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}

class HTTPHandler:

    def __init__(self, configuration):
        self.setup(configuration)
        self.echo = None
        if "ECHO" in configuration:
            self.echo = configuration['ECHO']
        if self.proxy_scheme is not None and self.proxy_host is not None and \
                        self.proxy_port is not None:
            credentials = ""
            if self.proxy_username is not None and self.proxy_password is not None:
                credentials = self.proxy_username + ":" + self.proxy_password + "@"
            proxyDict = {
                self.proxy_scheme: self.proxy_scheme + "://" + credentials +
                                                    self.proxy_host + ":" + self.proxy_port
            }

            proxy = urllib2.ProxyHandler(proxyDict)

            if credentials != '':
                auth = urllib2.HTTPBasicAuthHandler()
                opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
            else:
                opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)

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

    def query(self, string):
        """
        Perform a query
        Args:
           query (str): The SQL query
        Returns:
            bool: A success or failure response
        """
        concat_param = None

        if self.request_type == 'GET':
            concat_param = "?" + self.param + '=' + urllib.quote_plus(string)
        data = None

        if self.request_type == 'POST':
            data = self.param + '=' + urllib.quote_plus(string)
        #print self.url+"?" + self.param + '=' + string
        req = Request(
            self.url + concat_param,
            data=data,
            headers={
                'User-Agent': self.user_agent,
                'Referer': self.referer,
                "Accept": "text/html"})
        html = ''

        try:

            httpget = urllib2.urlopen(req)
            html = httpget.read()

        except urllib2.HTTPError as error:

            if error.code == 403:
                if self.block == None:
                    html = self.bypass
                elif self.bypass == None:
                    html = self.block
                else:
                    html = self.block + self.bypass
            else:
                print 'Can not connect. We failed with error code - %s.' % error.code
                exit()
        if self.echo:
            print self.echo
        if self.block is not None and self.block != "":
            pattern = r'' + re.escape(self.block)
            hits = re.findall(pattern, html)
            if len(hits) > 0:
                #print 'True'
                return True
            else:
                #print 'False'
                return False

        if self.bypass is not None and self.bypass != "":
            pattern = r'' + re.escape(self.bypass)
            hits = re.findall(pattern, html)
            if len(hits) > 0:
                return False
            else:
                return True

        print 'Please give either a BLOCK or a BYPASS pattern'
        exit(1)