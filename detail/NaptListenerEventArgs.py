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

class NaptListenerEventArgs(object):
    def __init__(self, accepted, accepter):
        self.accepted    = accepted
        self.accepter    = accepter
