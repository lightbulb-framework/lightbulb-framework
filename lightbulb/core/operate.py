"""This module is used for CLI module initialization and execution"""
import os
import inspect
from lightbulb.core.utils.ipc import  Pipe
from threading import Thread
import imp
import sys


META = {
    'author': 'George Argyros, Ioannis Stais',
    'name': 'MANAGE',
    'description': 'Executes Core Modules',
    'type': 'CORE',
        'options': [
            ('MODULE_A', None, True, 'File to save learned filter if no bypass is found', 5),
            ('MODULE_B', None, False, 'Handler for membership query function', 0),
       ],
    'comments': ['']
}


sys.path.insert(1, imp.find_module('lightbulb')[1]+'/modules')
sys.path.insert(1, imp.find_module('lightbulb')[1]+'/core/utils/')



def operate_learn(module, configuration):
    """
   Initiates the execution of a module
   Args:
       module (class): The module class to be initiated
       configuration (dict): The module options
   Returns:
       list: A list with the results and stats as tuples
   """
    initmodule = module(configuration)
    initmodule.learn()
    name, bypass = initmodule.getresult()
    return [(name, bypass)] + initmodule.stats()

def operate_diff_part(module, configuration, shared_memory, cross):
    """
    Initiates the execution of a module
    Args:
        module (class): The module class to be initiated
        configuration (dict): The module options
        shared_memory (list): A shared memory for intermodule communication
        cross (int): The identifier for this instance
    Returns:
        None
    """
    initmodule = module(configuration, shared_memory, cross)
    if cross == 1:
        shared_memory[4] = initmodule
        initmodule.learn()
        name, bypass = initmodule.getresult()
        shared_memory[6] = [(name, bypass)]+initmodule.stats()
    else:
        shared_memory[5] = initmodule
        initmodule.learn()

def operate_diff(module_class_A, configuration_A, module_class_B, configuration_B):
    """
    Initiates the execution of two modules in parallel
    Args:
        module_class_A (class): The module class to be initiated
        configuration_A (dict): The module options
        module_class_B (class): The module class to be initiated
        configuration_B (dict): The module options
    Returns:
        None
    """
    object_a = None
    object_b = None
    shared_a = None
    shared_b = None
    target_a = None
    target_b = None
    target_a_pipe, target_b_pipe = Pipe()
    result = []
    shared_memory = [target_a_pipe, target_b_pipe, object_a, object_b, shared_a, shared_b, result]

    target_a = Thread(target=operate_diff_part,
                      args=(module_class_A, configuration_A, shared_memory, 1))
    target_a.setDaemon(True)
    target_a.start()
    target_b = Thread(target=operate_diff_part,
                      args=(module_class_B, configuration_B, shared_memory, 2))
    target_b.setDaemon(True)
    target_b.start()
    while True:
        target_a.join(600)
        if not target_a.isAlive():
            target_a = None
            break
    print 'thread one finished'
    # End Cross _check
    target_b.join(0)
    target_b = None
    print 'thread two finished'
    return  shared_memory[6]


def manage(module_name, configuration):
    """
    This function manages the module initialization and execution
    Args:
        module_name (class): The module class to be initiated
        configuration (dict): The module options
    Returns:
       list: A list with the results and stats as tuples
    """

    module = __import__(module_name)
    classmembers = [classmodule for classmodule in inspect.getmembers(module, inspect.isclass)
                    if classmodule[0] == 'Module' or classmodule[0] == 'Module_A'
                    or classmodule[0] == 'Module_B']
    if len(classmembers) == 1:
        return  operate_learn(classmembers[0][1], configuration)
    else:
        if classmembers[0][0] == "Module_A":
            return operate_diff(classmembers[0][1], configuration, classmembers[1][1], configuration)
        else:
            return operate_diff(classmembers[1][1], configuration, classmembers[0][1], configuration)


