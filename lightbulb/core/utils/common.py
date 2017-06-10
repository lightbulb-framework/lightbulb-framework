"""This module contains common functions"""
import time
import os
import getpass
from os.path import expanduser
from symautomata.dfa import  DFA
import imp
import re

def accept_bool(user_input):
    """
        Transforms a string into bool
        Args:
            user_input (str): The string parameter
        Retuns:
            bool: A true or false value
    """
    if not isinstance(user_input, basestring):
        return  user_input

    if user_input.lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    else:
        return  False


def findlibrary(path):
    path = re.sub('.*my_saved_models/', expanduser("~") + "/.LightBulb/models/", path)
    path = re.sub('.*my_saved_regex/', expanduser("~") + "/.LightBulb/regex/", path)
    path = re.sub('.*my_saved_trees/', expanduser("~") + "/.LightBulb/trees/", path)
    path = re.sub('.*my_saved_grammars/', expanduser("~") + "/.LightBulb/grammars/", path)
    path = path.replace('{library}', imp.find_module('lightbulb')[1]+"/data/")
    return path

def save_model(save, model):
    if not isinstance(save, basestring):
        return
    if save == "REGEX":
        regex = model.to_regex()
        return "Regular Expression", regex
    elif save == "STRING":
        string = model.shortest_string()
        return "Shortest String", string
    elif save.lower() in ['true', '1', 't', 'y', 'yes']:
        home = expanduser("~")
        timestr = time.strftime("%Y%m%d-%H%M%S")
        if not os.path.exists(home+"/.LightBulb/"):
            os.makedirs(home+"/.LightBulb/")
        if not os.path.exists(home+"/.LightBulb/models"):
            os.makedirs(home+"/.LightBulb/models")
        model.save(home+"/.LightBulb/models/"+timestr+".fst")
        ruleset_file_meta = open(home+"/.LightBulb/models/"+timestr+".py", "w")
        ruleset_file_meta.write(
            "META = {\n\
                    'author': '"+getpass.getuser()+"',\n\
                    'description': 'Saved model on "+timestr+"',\n\
                    'type':'FST',\n\
                    'comments': []\n\
            }")
        ruleset_file_meta.close()
        return "Saved Model", home+"/.LightBulb/models/"+timestr+".fst"
    elif save.lower() in ['False', '2', 'f', 'n', 'no']:
        return
    else:
        model.save(save)
        return "Saved Model", save
