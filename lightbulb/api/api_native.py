import subprocess
import os
import sys

class LightBulb():
    """
    This class is an interface to lightbulb framework that can be used
    to extend its functionality. The included functions support the main
    functionalities of the framework, such as the GOFA, and SFADiff
    algorithm, and some modules.
    """

    def __init__(self):
        """
        Initialization function of the class. It creates instances
        of the lightbulb CLI show and use functionalities.
        """

        self.my_env = os.environ
        self.my_env["PYTHONPATH"] = sys.path[-2]



    def start_gofa_algorithm(self, path, configuration, handler, handlerconfig, func = None):
        """
        Starts the GOFA algorithm module
        Args:
            configuration (dict): The dictionary to be used as a parameter during
            the initialization of the GOFA class.
            handler (class): The class type to be used for membership
            requests.
            handlerconfig (dict): The dictionary to be used as a parameter during
            the initialization of the handler class.
        Returns:
            dict: The resulting statistics
        """
        process = subprocess.Popen(path, bufsize=1, universal_newlines=True, executable=None,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=None, preexec_fn=None, close_fds=True, shell=True,  env=self.my_env)
        print 'use ' + handler + ' as query_handler'
        process.stdin.write('use ' + handler + ' as query_handler\n')
        for x in handlerconfig:
            print 'define ' + x + ' ' + `handlerconfig[x]`
            process.stdin.write('define ' + x + ' ' + `handlerconfig[x]` + ' \n')
        process.stdin.write('back\n')

        print 'use GOFA as my_gofa\n'
        process.stdin.write('use GOFA as my_gofa\n')
        for x in configuration:
            if x == 'HANDLER':
                continue
            print 'define ' + x + ' ' + `configuration[x]`
            process.stdin.write('define ' + x + ' ' + `configuration[x]` + ' \n')
        process.stdin.write('define HANDLER query_handler \n')
        process.stdin.write('back\n')
        process.stdin.write('start my_gofa\n')
        process.stdin.write('\n')

        process.stdin.write('quit\n')

        stats = []

        lastline = ""
        for line in iter(process.stdout.readline, ''):
            lastline = line.rstrip()
            if func:
                func(lastline)
            print lastline
            if "| " == lastline[0:2] and "| Name" != lastline[0:6]:
                val = lastline[lastline[2:].find('|') + 3:-2].rstrip().lstrip().encode('ascii', 'ignore')
                if val == "None":
                    val = None
                stats.append((lastline[2:lastline[2:].find('|')].rstrip().lstrip().encode('ascii', 'ignore'),val))
        process.stdout.close()
        process.stdin.close()
        del process
        print 'ok'
        return stats

    def start_sfadiff_algorithm(
            self,
            path,
            configuration_a,
            configuration_b,
            handlerconfig_a,
            handlerconfig_b,
            handler_a,
            handler_b,
            func = None):
        """
        Starts the SFADiff algorithm module
        Args:
            configuration_a (dict): The dictionary to be used as a parameter during
            the initialization of the SFADiff class.
            configuration_b (dict): The dictionary to be used as a parameter during
            the initialization of the SFADiff class.
            handlerconfig_a (dict): The dictionary to be used as a parameter during
            the initialization of the handler class.
            handlerconfig_b (dict): The dictionary to be used as a parameter during
            the initialization of the handler class.
            handler_a (class): The class type to be used for membership
            requests.
            handler_b (class): The class type to be used for membership
            requests.
        Returns:
            dict: The resulting statistics
        """
        process = subprocess.Popen(path, bufsize=1, universal_newlines=True, executable=None,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=None, preexec_fn=None, close_fds=True, shell=True,  env=self.my_env)

        print 'use ' + handler_a + ' as query_handler_a'
        process.stdin.write('use ' + handler_a + ' as query_handler_a\n')
        for x in handlerconfig_a:
            print 'define ' + x + ' ' + `handlerconfig_a[x]`
            process.stdin.write('define ' + x + ' ' + `handlerconfig_a[x]` + ' \n')
        print 'back'
        process.stdin.write('back\n')

        print 'use ' + handler_b + ' as query_handler_b'
        process.stdin.write('use ' + handler_b + ' as query_handler_b\n')
        for x in handlerconfig_b:
            print 'define ' + x + ' ' + `handlerconfig_b[x]`
            process.stdin.write('define ' + x + ' ' + `handlerconfig_b[x]` + ' \n')
        print 'back'
        process.stdin.write('back\n')

        print 'use SFADIFF as my_sfadiff_a'
        process.stdin.write('use SFADIFF as my_sfadiff_a\n')
        for x in configuration_a:
            if x == 'HANDLER':
                continue
            print 'define ' + x + ' ' + `configuration_a[x]`
            process.stdin.write('define ' + x + ' ' + `configuration_a[x]` + ' \n')
        print 'define HANDLER query_handler_a'
        process.stdin.write('define HANDLER query_handler_a \n')
        print 'back'
        process.stdin.write('back\n')

        print 'use SFADIFF as my_sfadiff_b'
        process.stdin.write('use SFADIFF as my_sfadiff_b\n')
        for x in configuration_b:
            if x == 'HANDLER':
                continue
            print 'define ' + x + ' ' + `configuration_b[x]`
            process.stdin.write('define ' + x + ' ' + `configuration_b[x]` + ' \n')
        print 'define HANDLER query_handler_b'
        process.stdin.write('define HANDLER query_handler_b \n')
        print 'back'
        process.stdin.write('back\n')

        print 'start my_sfadiff_a my_sfadiff_b'
        process.stdin.write('start my_sfadiff_a my_sfadiff_b\n')
        process.stdin.write('\n')
        process.stdin.write('\n')

        process.stdin.write('quit\n')
        process.stdin.write('quit\n')
        stats = []
        lastline = ""
        for line in iter(process.stdout.readline, ''):
            lastline = line.rstrip()
            print lastline
            if func:
                func(lastline)
            if "| " == lastline[0:2] and "| Name" != lastline[0:6]:
                val = lastline[lastline[2:].find('|') + 3:-2].rstrip().lstrip().lstrip().encode('ascii', 'ignore')
                if val == "None":
                    val = None
                stats.append((lastline[2:lastline[2:].find('|')].rstrip().lstrip().encode('ascii', 'ignore'), val))

        process.stdout.close()
        process.stdin.close()
        del process
        return stats
