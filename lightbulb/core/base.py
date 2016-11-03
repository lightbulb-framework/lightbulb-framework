"""This module is used on every CLI operation"""
import os
import sys
import inspect
import imp
from symautomata.alphabet import createalphabet
sys.path.insert(1, imp.find_module('lightbulb')[1]+'/core/modules')
moduleNames = [name[:-3] for name in os.listdir(imp.find_module('lightbulb')[1]+'/core/modules')
               if name.endswith(".py")]


def options_as_dictionary(meta):
    """
    Transforms a list of tuples to a dictionary
    Args:
        meta (list): A list ot option tuples
    Retuns:
        dict: A dictionary of options key - values
    """
    module_config = {}
    for seltuple in meta:
        module_config.update({seltuple[0]: seltuple[1]})
    return  module_config

def importmodule(name):

    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def create_object(object_type, object_type_configuration, handler, handler_configuration):
    object_mod = importmodule('lightbulb.core.modules.' + object_type.lower())
    object_class = getattr(object_mod, object_type)
    handler_mod = importmodule('lightbulb.core.utils.' + handler.lower())
    handler_class = getattr(handler_mod, handler)
    class Module(object_class):
        def setup(self, configuration):
            super(Module,self).setup(configuration)
            self.handler = handler_class(handler_configuration)
    return  Module