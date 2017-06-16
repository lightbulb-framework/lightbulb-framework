import sys, os, inspect, imp

import jarray

class classPathHacker(object):
    """Original Author: SG Langer Jan 2007, conversion from Java to Jython
    Updated version (supports Jython 2.5.2) From http://glasblog.1durch0.de/?p=846

    Purpose: Allow runtime additions of new Class/jars either from
    local files or URL
    """
    import java.lang.reflect.Method
    import java.io.File
    import java.net.URL
    import java.net.URLClassLoader

    def addFile(self, s):
        """Purpose: If adding a file/jar call this first
        with s = path_to_jar"""
        # make a URL out of 's'
        f = self.java.io.File(s)
        u = f.toURL()
        a = self.addURL(u)
        return a

    def addURL(self, u):
        """Purpose: Call this with u= URL for
        the new Class/jar to be loaded"""
        sysloader = self.java.lang.ClassLoader.getSystemClassLoader()
        sysclass = self.java.net.URLClassLoader
        method = sysclass.getDeclaredMethod("addURL", [self.java.net.URL])
        a = method.setAccessible(1)
        jar_a = jarray.array([u], self.java.lang.Object)
        b = method.invoke(sysloader, [u])
        return u


class cursorClass():
	def __init__(self, inputstmt):
		self.stmt = inputstmt
		self.rs = None

	def execute(self, query):
		try:
			print 'MySQL executing: ',query
			self.rs = self.stmt.execute(query)
			print 'MySQL finish executing: ', query
		except:
			print 'MySQL received exception on executing: ', query
			return []
		
	def fetchall(self):
		try:
			return self.rs.fetchall()
		except:
			return []
		

class connClass():
	def __init__(self, inputstmt):
		self.stmt = inputstmt
		
	def autocommit(self, bool):
		pass

	def cursor(self):
		return cursorClass(self.stmt.cursor())



def connect(host, port, user, passwd, db):
	
	from com.ziclix.python.sql import zxJDBC

	jarLoad = classPathHacker()
	a = jarLoad.addFile(os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'mysql-connector-java-5.0.8-bin.jar'))

	from com.ziclix.python.sql import zxJDBC
	stmt = zxJDBC.connect("jdbc:mysql://"+host+":"+`port`+"/"+db, user, passwd,  'com.mysql.jdbc.Driver') 
	conn = connClass(stmt)
	print 'Connected to MySQL!'
	return conn



class Warning(Exception):
	def __init__(self):
		print 'MySQL Warning!'
		print Exception
		pass

class Error(Exception):
	def __init__(self):
		print 'MySQL Error!'
		print Exception
		pass


if __name__ == '__main__':
	handler = connect("127.0.0.1", 3306, "root", "root", "fuzzing")
	print 'connected'
	print 'getting  cursor'
	cursor = handler.cursor()
	print 'cursor ok'
	print 'testing execution'
	cursor.execute("DROP TABLE IF EXISTS `a`")
	print 'ok'
