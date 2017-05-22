"""This module handles the communication with the SQL database"""
import string
import MySQLdb
from lightbulb.core.utils.common import accept_bool

META = {
    'author': 'George Argyros, Ioannis Stais',
    'name':'SQLHandler',
    'description': 'Performs membership queries in MySQL parser',
    'type': 'UTIL',
    'options': [
        ('HOST', "127.0.0.1", True, 'The target host'),
        ('PORT', "3306", True, 'The target port'),
        ('USERNAME', None, True, 'The required username'),
        ('PASSWORD', None, True, 'The required password'),
        ('DATABASE', None, True, 'The MySQL database'),
        ('PREFIX_QUERY', None, True, 'The sql query to be concatenated'),
        ('SQLPARSE', True, True, 'Positive response if sql parses a query payload'),
        ('ECHO', None, False, 'Optional custom debugging message that is printed on each membership request'),
    ],
    'comments': ['Sample comment 1', 'Sample comment 2']
}

class SQLHandler():
    """This class handles the communication with the MySQL database"""
    conn = None
    cursor = None
    TABLES = {}
    INSERT = {}
    DROP = {}
    DROP['a'] = ("DROP TABLE IF EXISTS `a`")

    TABLES['a'] = (
        " CREATE TABLE `a` ("
        "  `id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `a` varchar(14) NOT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB")

    INSERT['a'] = ("INSERT INTO a (a) VALUES('a')")


    def connect(self, db_config):
        """
        Connect to MySQL database
        Args:
            db_config (dict): A dictionary containing the configuration
        Returns:
            (Mysql Connector): The established MySQL connection
        """
        try:
            print 'Connecting to MySQL database:',
            self.conn = MySQLdb.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                passwd=db_config['passwd'],
                db=db_config['db'])
            print 'OK'
            self.conn.autocommit(True)
            self.cursor = self.conn.cursor()
            return self.conn
        except MySQLdb.Error as error:
            print error
            return 0

    def query_database(self, query):
        """
        Perform a database query
        Args:
            query (str): The SQL query
        Returns:
            list: Mysql Rows
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except MySQLdb.Error as err:
            # print("Failed executing query: {}".format(err))
            return 0
        except MySQLdb.Warning as wrn:
            return 0

    def initialize(self):
        """Initialize SQL database in the correct state"""
        for name, ddl in self.DROP.iteritems():
            try:
                print "Drop table {}:".format(name),
                self.cursor.execute(ddl)
            except MySQLdb.Error as err:
                print err
            except MySQLdb.Warning as wrn:
                pass
            finally:
                print 'OK'
        for name, ddl in self.TABLES.iteritems():
            try:
                print "Creating table {}:".format(name),
                self.cursor.execute(ddl)
            except MySQLdb.Error as err:
                print err
            except MySQLdb.Warning as wrn:
                pass
            finally:
                print 'OK'
        for name, ddl in self.INSERT.iteritems():
            try:
                print "Inserting into table {}:".format(name),
                self.cursor.execute(ddl)
            except MySQLdb.Error as err:
                print err
            except MySQLdb.Warning as wrn:
                pass
            finally:
                print 'OK'

    def testquery(self):
        """Perform a test query"""
        print 'Test query:',
        rows = self.query_database('SELECT * FROM a')
        if rows == 0:
            print 'FAIL'
            return
        if len(rows) < 1:
            print 'FAIL'
            return
        if rows[0][0] != 1:
            print 'FAIL'
            return
        if rows[0][1] != 'a':
            print 'FAIL'
            return
        print 'OK'

    def testfailquery(self):
        """Perform a test query that will fail"""
        print 'Test wrong query:',
        rows = self.query_database('SELECTA * FROM a')
        if rows == 0:
            print 'OK'
            return
        print 'FAIL'

    def close(self):
        """Terminate Connection"""
        pass

    def query(self, query):
        """
        Perform a query
        Args:
           query (str): The SQL query
        Returns:
            bool: A success or failure response
        """
        rows = self.query_database(string.replace(self.prefix_query, '**', query))
        if self.echo:
            print self.echo
        if rows == False:
            # print 'Request: '+string.replace(self.initquery, '**', query)+'
            # (FALSE)'
            if self.sqlparse:
                return  False
            else:
                return True
        elif len(rows) == 1:
            # print 'Request: '+string.replace(self.initquery, '**', query)+'
            # (FALSE)'
            if self.sqlparse:
                return  False
            else:
                return True
        elif len(rows) > 1:
            print 'Request: ' + string.replace(self.prefix_query, '**', query) + ' (TRUE)'
            if self.sqlparse:
                return  False
            else:
                return True
        else:
            # print len(rows)
            # print 'Request: '+string.replace(self.initquery, '**', query)+'
            # (SPECIAL FALSE)'
            if self.sqlparse:
                return  False
            else:
                return True

    def __init__(self, configuration):
        """Initialize class
        Args:
            host (str): The MySQL server host
            port (str): The MySQL server port
            user (str): The required username
            passwd (str): The required password
            database (str): The MySQL database to be used
            initquery (str): The query that will be concatenated in all requests
        Returns:
            None
        """
        self.setup(configuration)
        self.echo = None
        if "ECHO" in configuration:
            self.echo = configuration['ECHO']
        self.port = int(self.port)
        self.sqlparse = accept_bool(self.sqlparse)
        db_config = {}
        db_config['host'] = self.host
        db_config['port'] = self.port
        db_config['user'] = self.username
        db_config['passwd'] = self.password
        db_config['db'] = self.database
        self.connect(db_config)
        self.initialize()
        self.testquery()
        self.testfailquery()

    def setup(self, configuration):
        self.sqlparse = configuration['SQLPARSE']
        self.prefix_query = configuration['PREFIX_QUERY']
        self.host = configuration['HOST']
        self.port = configuration['PORT']
        self.username = configuration['USERNAME']
        self.password = configuration['PASSWORD']
        self.database = configuration['DATABASE']

if __name__ == '__main__':
    handler = SQLHandler('config.ini', '')
