# Copyright (c) 2008, Christian Heimes
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of author nor the names of any contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
"""Monkey patch collection
"""
import sys
import threading
from __builtin__ import property as bltin_property

__all__ = ("property", "monkey",)

property = None

# Python 2.6 style property class
class property26(bltin_property):
    def getter(self, fget):
        return property(fget, self.fset, self.fdel, self.__doc__)
    def setter(self, fset):
        return property(self.fget, fset, self.fdel, self.__doc__) 
    def deleter(self, fdel):
        return property(self.fget, self.fset, fdel, self.__doc__)


class ThreadPatch(object):
    """Monkey patch for threading.Thread
    """
    is_alive = threading.Thread.isAlive.im_func
    
    name = bltin_property(threading.Thread.getName.im_func, 
                          threading.Thread.setName.im_func)
    daemon = bltin_property(threading.Thread.isDaemon.im_func,
                            threading.Thread.setDaemon.im_func)


class ConditionPatch(object):
    """Monkey patch for threading._Condition
    """
    notify_all = threading._Condition.notifyAll.im_func

    
def monkey():
    """Monkey patch
    """
    global property
    
    if property is not None:
        return
    elif sys.version_info >= (2, 6):
        property = bltin_property
        return
    
    property = property26

    if ThreadPatch not in threading.Thread.__bases__: 
        threading.Thread.__bases__ += (ThreadPatch,)

    if ConditionPatch not in threading._Condition.__bases__:
        threading._Condition.__bases__ += (ConditionPatch,)
        
    threading.current_thread = threading.currentThread
