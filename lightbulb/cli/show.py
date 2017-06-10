"""This module contains all the functions that present data for the CLI"""
import logging
import os
import sys
import imp
from os.path import expanduser
from lightbulb.core.base import importmodule

from cliff.lister import Lister

class Modules(Lister):
    "Shows available application modules"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        """
        Returns available application module
        Args:
            None
        Returns:
            tuple: Available application modules
        """
        module_names = [name[:-3] for name in os.listdir(imp.find_module('lightbulb')[1]+'/modules')
                        if name.endswith(".py")]
        self.app.stdout.write('\n\nAvaliable Modules:\n')
        data = []
        for module_name in module_names:
            try:
                meta = importmodule('lightbulb.modules.' + module_name).META
                data.append((module_name, meta['description']))
            except:
                pass
        return (('Name', 'Value'), (data))

class Core(Lister):
    "Shows available core modules"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        """
        Returns available application module
        Args:
            None
        Returns:
            tuple: Available application modules
        """
        module_names = [name[:-3] for name in os.listdir(imp.find_module('lightbulb')[1] + '/core/modules')
                        if name.endswith(".py")]
        self.app.stdout.write('\n\nAvaliable Core Modules:\n')
        data = []
        for module in module_names:
            try:
                meta = importmodule('lightbulb.core.modules.' + module).META
                data.append((meta['name'], meta['description']))
            except:
                pass
        return (('Name', 'Value'), (data))

class Utils(Lister):
    "Shows available core modules"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        """
        Returns available application module
        Args:
            None
        Returns:
            tuple: Available application modules
        """
        module_names = [name[:-3] for name in os.listdir(imp.find_module('lightbulb')[1] + '/core/utils/')
                        if name.endswith(".py")]
        self.app.stdout.write('\n\nAvaliable Utilities Modules:\n')
        data = []
        for module in module_names:
            try:
                meta = importmodule('lightbulb.core.utils.' + module).META
                data.append((meta['name'], meta['description']))
            except:
                pass
        return (('Name', 'Value'), (data))

class Info(Lister):
    """
    Returns information about a core or library module
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(Info, self).get_parser(prog_name)
        parser.add_argument('module', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Returns information about a module
        Args:
            parsed_args.module (str): The requested module
        Returns:
            tuple: Core or Application module details
        """
        module_name = parsed_args.module
        self.app.stdout.write('\n\nModule ' + module_name + ' Information:\n')

        found = 0

        # First check if module is in CORE modules
        try:
            meta = importmodule('lightbulb.core.modules.'+module_name.lower()).META
        except:
            try:
                meta = importmodule('lightbulb.core.utils.'+module_name.lower()).META
            except:
        # If not found, continue to user modules
                try:
                    meta = importmodule('lightbulb.modules.' + module_name).META
                except:
                    print 'Not found'
                    return (('Name', 'Value'),
                    ([]))

        return (('Name', 'Value'),
                ([('Author', meta['author']),
                  ('Description', meta['description']),
                  ('Comments', ', '.join(meta['comments']))]))


class LibraryModules(Lister):
    "Shows available library modules"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(LibraryModules, self).get_parser(prog_name)
        parser.add_argument('folder', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Returns available library modules
        Args:
            None
        Returns:
            tuple: Available library modules
        """
        folder = parsed_args.folder
        if len(folder) > 0 and folder[0] == '/':
            folder = folder[1:]
        if len(folder) > 1 and folder[0:2] == './':
            folder = folder[2:]

        path = imp.find_module('lightbulb')[1]+'/data/' + folder
        if folder == "my_saved_models":
            path = expanduser("~")+"/.LightBulb/models/"
        if folder == "my_saved_regex":
            path = expanduser("~")+"/.LightBulb/regex/"
        if folder == "my_saved_trees":
            path = expanduser("~")+"/.LightBulb/trees/"
        if folder == "my_saved_grammars":
            path = expanduser("~")+"/.LightBulb/grammars/"
        data = []
        # First check if module is in CORE modules
        sys.path.insert(1, os.path.join(sys.path[0], path))
        module_names = [name[:-3] for name in os.listdir(path)
                        if name.endswith(".py") and name != "__init__.py"]

        for module_name in module_names:
            meta = importmodule(module_name).META
            data.append((module_name, meta['description'], meta['type']))
        if folder == ".":
            data.append(("my_saved_models", "My saved models", "Folder"))
            data.append(("my_saved_regex", "My saved regex", "Folder"))
            data.append(("my_saved_trees", "My saved trees", "Folder"))
            data.append(("my_saved_grammars", "My saved grammars", "Folder"))

        return (('Name', 'Value', 'Type'), (data))

class LibraryInfo(Lister):
    """
    Returns information about a library module
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(LibraryInfo, self).get_parser(prog_name)
        parser.add_argument('component', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Returns information about a library module
        Args:
            None
        Returns:
            tuple: Library module details
        """
        component = parsed_args.component

        component_splitted = component.split('/')
        for component in component_splitted:
            if component == '.':
                component_splitted.remove(component)
        module_name = component_splitted[-1]
        folder = "/".join(component_splitted[:-1])
        path = imp.find_module('lightbulb')[1]+'/data/'+ folder
        if folder == "my_saved_models":
            path = expanduser("~")+"/.LightBulb/models/"
        if folder == "my_saved_regex":
            path = expanduser("~")+"/.LightBulb/regex/"
        if folder == "my_saved_trees":
            path = expanduser("~")+"/.LightBulb/trees/"
        if folder == "my_saved_grammars":
            path = expanduser("~")+"/.LightBulb/grammars/"
        # First check if module is in CORE modules
        sys.path.insert(1, os.path.join(sys.path[0], path))
        meta = importmodule(module_name).META

        self.app.stdout.write('\n\nComponent ' + module_name + ' Information:\n')

        if meta['type'] == 'Grammar' or meta['type'] == 'Regex':
            path = ('Path', path +"/"+ module_name + '.y')
        elif meta['type'] == 'Configuration':
            path = ('Path', path +"/"+ module_name + '.json')
        elif meta['type'] == 'FST':
            path = ('Path', path + module_name + '.fst')
        else:
            path = ('Path', path +"/"+ module_name)
        return (('Name', 'Value'),
                ([('Author', meta['author']),
                  ('Description', meta['description']),
                  ('Type', meta['type']), path,
                  ('Comments', ', '.join(meta['comments']))]))

class LibraryCat(Lister):
    """
    Returns the content of a library module
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(LibraryCat, self).get_parser(prog_name)
        parser.add_argument('component', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Returns the content of a library module
        Args:
            None
        Returns:
            tuple: Library module content
        """
        component = parsed_args.component

        component_splitted = component.split('/')
        module_name = component_splitted[-1]
        for component in component_splitted:
            if component == '.':
                component_splitted.remove(component)
        folder = "/".join(component_splitted[:-1])
        path = imp.find_module('lightbulb')[1]+'/data/'+ folder
        if folder == "my_saved_models":
            path = expanduser("~")+"/.LightBulb/models/"
        if folder == "my_saved_regex":
            path = expanduser("~")+"/.LightBulb/regex/"
        if folder == "my_saved_trees":
            path = expanduser("~")+"/.LightBulb/trees/"
        if folder == "my_saved_grammars":
            path = expanduser("~")+"/.LightBulb/grammars/"

        # First check if module is in CORE modules
        sys.path.insert(1, os.path.join(sys.path[0], path))
        meta = importmodule(module_name).META

        self.app.stdout.write('\n\nComponent ' + module_name + ' Information:\n')

        content = ""
        if meta['type'] == 'Grammar' or meta['type'] == 'Regex':
            with open(path +"/"+ module_name + '.y') as grammaregex_file:
                content = grammaregex_file.read()
        elif meta['type'] == 'Configuration' or meta['type'] == 'Tree':
            with open(path +"/"+ module_name + '.json') as conf_file:
                content = conf_file.read()
        else:
            content = 'This is a folder and the command cannot be used.'
        return (('Name', 'Value'), ([(module_name, content)]))


class LibrarySearch(Lister):
    "Searches available library modules for keywords"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """
        Argument parser
        Args:
            prog_name (object): The current program
        Returns:
            object: A parser for the provided arguments
        """
        parser = super(LibrarySearch, self).get_parser(prog_name)
        parser.add_argument('keywords', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        """
        Returns matched library modules
        Args:
            parsed_args.keywords (str): Comma separated keywords
        Returns:
            tuple: Matched library modules
        """
        keywords = parsed_args.keywords.split(',')
        data = []
        queue = [imp.find_module('lightbulb')[1]+'/data/']
        for folder in queue:
            sys.path.insert(1, os.path.join(sys.path[0], folder))
            module_names = [name[:-3] for name in os.listdir(folder)
                            if name.endswith(".py") and name != "__init__.py"]
            folders = [os.path.join(folder,o) for o in os.listdir(folder) if os.path.isdir(os.path.join(folder,o))]
            for newfolder in folders:
                queue.append(newfolder)
            for module_name in module_names:
                meta = importmodule(module_name).META
                for keyword in keywords:
                    if keyword in meta['description'] or keyword in module_name:
                        component = folder + '/'+module_name
                        if meta['type'] == 'Grammar' or meta['type'] == 'Regex':
                            path = imp.find_module('lightbulb')[1]+'/data/' + component + '.y'
                        elif meta['type'] == 'Configuration':
                            path = imp.find_module('lightbulb')[1]+'/data/' + component + '.json'
                        else:
                            path = imp.find_module('lightbulb')[1]+'/data/' + component
                        data.append((module_name, meta['description'], meta['type'], path))
                        break
        return (('Name', 'Value', 'Type', 'Path'), (data))