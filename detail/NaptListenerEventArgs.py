#!/usr/bin/env python
# -*- coding: utf-8 -*-

class NaptListenerEventArgs(object):
    def __init__(self, accepted, accepter):
        self.accepted    = accepted
        self.accepter    = accepter
