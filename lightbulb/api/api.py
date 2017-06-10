"""
This file offers an interface to lightbulb framework that can be
used to extend its functionality. The main difference with the CLIFF
interface is that it allows you to include your own handlers
(e.g. HTTP handler) without having to insert them as Modules in
lightbulb's installation folder.
"""
import sys
import imp
import logging
from cliff.app import App
from cliff.commandmanager import CommandManager
from lightbulb.cli.show import LibraryModules, LibraryCat
from lightbulb.cli.use import StartSaved, Use, Define, Back
from lightbulb.core.operate import operate_learn, operate_diff
from lightbulb.core.utils.common import findlibrary
from lightbulb.core.base import importmodule
from lightbulb.api.gentree import GenerateTree


class Cliffargs(object):
    """
    This class is used to emulate the CLIFF arguments' class
    that is filled automatically with user's inputs
    in the interactive console.
    """
    folder = None
    component = None
    module = None
    set = None


class LightBulb(App):
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
        super(LightBulb, self).__init__(
            description='LightBulb App',
            version='0.1',
            command_manager=CommandManager('cliff.lightbulb'),
            deferred_help=False,
        )
        self.library = LibraryModules(self, self, None)
        self.librarycat = LibraryCat(self, self, None)
        self.startsaved = StartSaved(self, self, None)
        self.use = Use(self, self, None)
        self.back = Back(self, self, None)
        self.define = Define(self, self, None)

    def readlibrary(self, folder, regex_func, grammar_func, tree_func):
        """
        THe function reads recursively a provided folder, and
         it triggers one of the provided functions for each file
         that it finds.
        Args:
            folder (str): The folder to read
            regex_func (func): Function to call when a regex is found.
            grammar_func (func): Function to call when a grammar is found.
            tree_func (func): Function to call when a tree is found.
        Returns:
            None
        """
        target = Cliffargs()
        target.folder = folder
        try:
            details = self.library.take_action(target)[1]
            if len(details) > 0:
                for found_file in details:
                    print found_file
                    if found_file:
                        if found_file[2] == 'Folder':
                            self.readlibrary(
                                folder + "/" + found_file[0], regex_func, grammar_func, tree_func)
                        if found_file[2] == 'Regex':
                            regex_func(
                                found_file, folder + "/" + found_file[0])
                        if found_file[2] == 'Grammar':
                            grammar_func(
                                found_file, folder + "/" + found_file[0])
                        if found_file[2] == 'Tree':
                            tree_func(found_file, folder + "/" + found_file[0])
        except:
            logging.debug('Error at readlibrary() in folder: ' + folder)
            logging.debug(sys.exc_info())

    def readlibraryfile(self, requestedfile):
        """
        Returns the contents of a provided file. The user gives
        the file location, and the function returns a tuple containing
        the name of the file and the contents of the file.
        Args:
            requestedfile (str): The file to be read.
        Returns:
            tuple (name, value): The file contents
        """
        target = Cliffargs()
        target.component = requestedfile
        details = self.librarycat.take_action(target)
        return details

    def create_object(
            self,
            object_type,
            handler_class,
            handler_configuration):
        """
        Initializes the provided handler and assigns it to
        a selected class type as parameter.
        Args:
            object_type (class): The object class to be returned (GOFA, SFADiff)
            handler_class (class): The handler class instance to be created
            and set as object class variable.
            handler_configuration (dict): The dictionary to be set as class variables in
            handler.
        Returns:
            class: The class type having an initialized handler
            as a class variable.
        """
        sys.path.insert(1, imp.find_module('lightbulb')[1] + '/modules')
        sys.path.insert(1, imp.find_module('lightbulb')[1] + '/core/utils/')
        sys.path.insert(1, imp.find_module('lightbulb')[1] + '/core/modules/')
        object_mod = importmodule(object_type.lower())
        try:
            object_class = getattr(object_mod, object_type)

            class Module(object_class):
                """
                The object class to be returned (GOFA, SFADiff)
                """

                def setup(self, configuration):
                    """
                    Overides the setup function in order to set
                    the handler instance as class variable
                    Args:
                        configuration (dict): The dictionary to be used
                        as input in the default setup function of the
                        class
                    Returns:
                        None
                    """
                    super(Module, self).setup(configuration)
                    self.handler = handler_class(handler_configuration)
        except:
            object_class = getattr(object_mod, "Module")
            if object_type == "distinguish_waf":

                class Module(object_class):
                    """
                    The object class to be returned (distinguish_waf)
                    """

                    def __init__(self, configuration):
                        """
                        Overides the init constructor in order to set
                        the handler instance as class variable
                        Args:
                            configuration (dict): The dictionary to be used
                            as input in the default setup function of the
                            class
                        Returns:
                            None
                        """
                        self.distinguisher = None
                        self.loadfile(findlibrary(configuration['FILE']))
                        self.httphandler = handler_class(handler_configuration)
                        self.name = None
                        self.queries = 0
            else:
                class Module(object_class):
                    """
                    The object class to be returned (any other)
                    """
                    pass

        return Module

    def start_gofa_algorithm(self, configuration, handler, handlerconfig):
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
        learningobject = self.create_object(
            "GOFA", handler, handlerconfig)
        try:
            return operate_learn(learningobject, configuration)
        except:
            logging.debug('Error in operate_learn()')
            logging.debug('Current configuration: ')
            logging.debug(configuration)
            logging.debug(sys.exc_info())
        return []

    def start_sfadiff_algorithm(
            self,
            configuration_a,
            configuration_b,
            handlerconfig_a,
            handlerconfig_b,
            hanlder_a,
            handler_b):
        print configuration_a
        print configuration_b
        print handlerconfig_a
        print handlerconfig_b
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
        learningobject_a = self.create_object(
            "SFADiff", hanlder_a, handlerconfig_a)
        learningobject_b = self.create_object(
            "SFADiff", handler_b, handlerconfig_b)
        try:
            return operate_diff(
                learningobject_a,
                configuration_a,
                learningobject_b,
                configuration_b)
        except:
            print 'Error in operate_diff()'
            print sys.exc_info()
            logging.debug('Error in operate_diff()')
            logging.debug('Current configuration:')
            logging.debug(configuration_a)
            logging.debug(configuration_b)
            logging.debug(sys.exc_info())
        return []

    def start_distinguishing_module(
            self,
            configuration,
            handler,
            handlerconfig):
        """
        Starts the distinguish module
        Args:
            configuration (dict): The dictionary to be used as a parameter during
            the initialization of the distinguish module.
            handler (class): The class type to be used for membership
            requests.
            handlerconfig (dict): The dictionary to be used as a parameter during
            the initialization of the handler class.
        Returns:
            dict: The resulting statistics
        """
        learningobject = self.create_object(
            "distinguish_waf",
            handler,
            handlerconfig)
        try:
            return operate_learn(learningobject, configuration)
        except:
            logging.debug('Error in distinguish()')
            logging.debug('Current configuration: ')
            logging.debug(configuration)
            logging.debug(sys.exc_info())
        return []

    def start_treegeneration_module(self, configuration):
        """
        Starts the tree generation module
        Args:
            configuration (dict): The dictionary to be used as a parameter during
            the initialization of the distinguish module.
        Returns:
            dict: The resulting statistics
        """
        return operate_learn(GenerateTree, configuration)
