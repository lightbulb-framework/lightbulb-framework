"""This module contains all the functions that perform an operation for the CLI"""
import logging
import sys
import os
import imp
from cliff.command import Command
from cliff.lister import Lister
from lightbulb.core.operate import manage, operate_diff, operate_learn
from lightbulb.core.base import options_as_dictionary, importmodule, create_object
import inspect

CURRENT = None
HANDLER = None
CORE = None
TYPE = None
MEMORY = {}
CONFIG = {}
META = None

def update_in_alist(alist, key, value):
    """Updates a value in a list of tuples"""
    return [(k, v1, v2, v3) if (k != key) else (key, value, v2, v3) for (k, v1, v2, v3) in alist]

def update_in_alist_inplace(alist, key, value):
    """Updates a list of tuples in place"""
    alist[:] = update_in_alist(alist, key, value)

def check_parameters(config):
    """
    Checks if all required parameters have been set
    Args:
        meta (list): A list of option tuples
    Returns:
        list: A list of option tuples that have not been set
    """
    required = []
    for option in META:
        if option[2] is True and (option[0] not in CONFIG or CONFIG[option[0]] is None):
            required.append((option[0], option[1], option[2]))
    return required

class Use(Command):
    "Entes in an application or core module view"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(Use, self).get_parser(prog_name)
        parser.add_argument('module', nargs='*', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Enters in an application or core module view
        Args:
            parsed_args.module (str): The requested module
        Returns:
            None
        """
        global CURRENT, CONFIG, META, HANDLER, CORE, TYPE
        if len(parsed_args.module) >= 1:
            module_name = parsed_args.module[0].lower()
            if len(parsed_args.module) >= 2:
                if parsed_args.module[1].lower() == 'as':
                    save_module_name = parsed_args.module[2].lower()
                else:
                    print 'The correct syntax is: use MODULE or use MODULE as my_module_1'
                    return  False
            else:
                save_module_name = module_name
            print module_name, save_module_name
            try:
                META = importmodule('lightbulb.modules.'+module_name).META['options']
                self.app.stdout.write('Entering module ' + module_name + '\n')
                CURRENT = save_module_name
                TYPE = module_name
            except:
                META = []
                try:
                    name = importmodule('lightbulb.core.utils.'+module_name).META['name']
                    self.app.stdout.write('Entering handler ' + module_name + '\n')
                    metatemp = importmodule('lightbulb.core.utils.'+module_name).META['options']
                    HANDLER = save_module_name
                    TYPE = name
                    for option in metatemp:
                        META.append((option[0], option[1], option[2], option[3]))
                except:
                    META = []
                    try:
                        name = importmodule('lightbulb.core.modules.' + module_name).META['name']
                        self.app.stdout.write('Entering core module ' + module_name + '\n')
                        metatemp = importmodule('lightbulb.core.modules.' + module_name).META['options']
                        CORE = save_module_name
                        TYPE = name
                        for option in metatemp:
                            META.append((option[0], option[1], option[2], option[3]))
                    except:
                        pass
                # for module_name in modules:
                # META = importmodule(module_name).META['options']
            if len(META) == 0:
                self.app.stdout.write('Module name was not found in modules\n')
                HANDLER = None
                META = None
                CORE = None
                TYPE = None
                return False
            else:
                configuration = options_as_dictionary(META)
                for option in configuration:
                    if option not in CONFIG:
                        CONFIG[option] = configuration[option]
            return  True

class Library(Command):
    "Entes in library view"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(Library, self).get_parser(prog_name)
        parser.add_argument('module', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Enters in library view
        """
        pass

class Define(Command):
    "Sets an option value"

    log = logging.getLogger(__name__)


    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(Define, self).get_parser(prog_name)
        parser.add_argument('set', nargs='*', default='.')
        return parser

    def take_action(self, parsed_args):
        global CONFIG
        """
        Sets an option value
        Args:
            parsed_args.set[0] (str): The requested option
            parsed_args.set[1] (str): The new value
        Returns:
            None
        """
        CONFIG[parsed_args.set[0]] =  (' '.join(parsed_args.set[1:])).strip()

        print "Option "+parsed_args.set[0]+' defined as '+(' '.join(parsed_args.set[1:])).strip()


class Back(Command):
    "Moves back to main menu view"

    log = logging.getLogger(__name__)


    def take_action(self, parsed_args):
        """
        Moves back to main menu view
        """
        global  CURRENT, META, HANDLER, MEMORY, CORE, TYPE
        print 'Back to main menu '
        if HANDLER:
            save_configuration = {x:CONFIG[x] for x in options_as_dictionary(META)}
            MEMORY[HANDLER] = {'TYPE':TYPE, 'CONFIG':save_configuration}
        if CORE:
            save_configuration = {x:CONFIG[x] for x in options_as_dictionary(META)}
            MEMORY[CORE] = {'TYPE':TYPE, 'CONFIG':save_configuration}
        CURRENT = None
        META = None
        HANDLER = None
        TYPE = None
        CORE = None
        #print MEMORY

class LibraryBack(Command):
    "Moves back to previous view"

    log = logging.getLogger(__name__)


    def take_action(self, parsed_args):
        """
        Moves back to previous view
        """
        global  CURRENT, META
        if CURRENT:
            print 'Back to module '+CURRENT
            print "\n"
        else:
            print 'Back to main menu '
            CURRENT = None
            META = None
            print "\n"

class Info(Lister):
    """
    Returns information about currently used module
    """
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        """
        Returns information about the currently used module
        Args:
            parsed_args.module (str): The requested module
        Returns:
            tuple: Details about the module
        """
        global  HANDLER, CORE


        found = 0

        # First check if module is in CORE modules
        try:
            meta = importmodule('lightbulb.core.modules.' + CORE.lower()).META
        except:
            try:
                meta = importmodule('lightbulb.core.utils.' + HANDLER.lower()).META
            except:
                # If not found, continue to user modules
                try:
                    meta = importmodule('lightbulb.modules.' + CURRENT).META
                except:
                    print 'Not found'
                    return (('Name', 'Value'),
                            ([]))

        return (('Name', 'Value'),
                ([('Author', meta['author']),
                  ('Description', meta['description']),
                  ('Comments', ', '.join(meta['comments']))]))

class Start(Lister):
    """Initiates the currently used module"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(Start, self).get_parser(prog_name)
        for argument in CONFIG:
            parser.add_argument('--'+argument, nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Initiates the currently used module
        Args:
            Option values with the prefix "--" (str): The requested option values
        Returns:
            tuple: The execution results and stats
        """
        if HANDLER != None:
            print 'Currently there is a selected Handler. Handlers can not be started'
            return False
        for argument in CONFIG:
            if getattr(parsed_args, argument) != '.':
                CONFIG[argument] = getattr(parsed_args, argument)
        parameters = check_parameters(CONFIG)
        if parameters != []:
            print 'The following parameters are required:\n'
            return (('Name', 'Value', 'Required'), (parameters))
        module_name = CURRENT
        self.app.stdout.write('Starting ' + module_name + ':\n')
        stats = manage(module_name, CONFIG)
        print '\n\nStatistics:\n'
        return (('Name', 'Value'), (stats))

class StartSaved(Lister):
    """Initiates the currently used module"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(StartSaved, self).get_parser(prog_name)
        parser.add_argument('module_a', nargs='?', default='.')
        parser.add_argument('module_b', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Initiates the currently used module
        Args:
            Option values with the prefix "--" (str): The requested option values
        Returns:
            tuple: The execution results and stats
        """
        global MEMORY
        module_a = getattr(parsed_args, 'module_a')
        module_b = getattr(parsed_args, 'module_b')
        if module_a != '.' and module_a not in MEMORY:
            print module_a + ' is not defined'
            return False
        if module_b != '.' and module_b not in MEMORY:
            print module_b + ' is not defined'
            return False
        if module_a != '.' and module_b != '.':
            self.app.stdout.write('Starting ' + module_a + ' and '+ module_b + ':\n')
            stats = operate_diff(create_object(MEMORY[module_a]['TYPE'],MEMORY[module_a]['CONFIG'], MEMORY[MEMORY[module_a]['CONFIG']['HANDLER']]['TYPE'], MEMORY[MEMORY[module_a]['CONFIG']['HANDLER']]['CONFIG']), MEMORY[module_a]['CONFIG'], create_object(MEMORY[module_b]['TYPE'],MEMORY[module_b]['CONFIG'], MEMORY[MEMORY[module_b]['CONFIG']['HANDLER']]['TYPE'], MEMORY[MEMORY[module_b]['CONFIG']['HANDLER']]['CONFIG']), MEMORY[module_b]['CONFIG'])
        elif module_a != '.':
            self.app.stdout.write('Starting ' + module_a + ':\n')
            stats = operate_learn(create_object(MEMORY[module_a]['TYPE'],MEMORY[module_a]['CONFIG'], MEMORY[MEMORY[module_a]['CONFIG']['HANDLER']]['TYPE'], MEMORY[MEMORY[module_a]['CONFIG']['HANDLER']]['CONFIG']), MEMORY[module_a]['CONFIG'])
        print '\n\nStatistics:\n'
        return (('Name', 'Value'), (stats))

class Options(Lister):
    "Shows the available options for the currently used module"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        """
        Shows the available options for the currently used module
        Args:
            None
        Returns:
            tuple: Module's options
        """
        module_name = CURRENT
        data = [(name, value, required, description) for name, value, required, description in META]
        for option in CONFIG:
            update_in_alist_inplace(data, option, CONFIG[option])
        return (('Name', 'Value', 'Required', 'Description'), (data))

class Error(Command):
    "Always raises an error"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('Causing error')
        raise RuntimeError('this is the expected exception')


class LibrarySubmit(Command):
    "Submits a custom library module to library repository"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        "Submits a custom library module to library repository"
        pass


class LibrarySync(Command):
    "Updates current library modules from repository"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        "Updates current library modules from repository"
        pass