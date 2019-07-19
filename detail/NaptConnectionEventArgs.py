#!/usr/bin/env python
# -*- coding: utf-8 -*-
    
class NaptConnectionEventArgs(object):
    def __init__(self, conn, data = None, offset = 0, size = 0):
        self.connection  = conn
        self.data        = data
        self.offset      = offset
        self.size        = size
