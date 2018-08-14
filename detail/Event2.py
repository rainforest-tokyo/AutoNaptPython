#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Event2(object):
    def __init__(self, doc = None):
        self.handlers = []
        self.__doc__ = doc

    def __str__(self):
        return 'Event<%s>' % str(self.__doc__)
    
    def add(self, handler):
        self.handlers.append(handler)
        return self
    
    def remove(self, handler):
        self.handlers.remove(handler)
        return self
    
    def __call__(self, sender, e):
        for handler in self.handlers:
            handler(sender, e)
    
    __iadd__ = add
    __isub__ = remove
