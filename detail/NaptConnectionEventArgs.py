#!/usr/bin/env python
# -*- coding: utf-8 -*-
    
#-----------------------------------
# AutoNaptPython 
#
# Copyright (c) 2018 RainForest
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#-----------------------------------

class NaptConnectionEventArgs(object):
    def __init__(self, conn, data = None, offset = 0, size = 0):
        self.connection  = conn
        self.data        = data
        self.offset      = offset
        self.size        = size
