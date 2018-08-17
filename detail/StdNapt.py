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

import os
import sys
import socket
import time
import datetime
from Utils import Utils

try:
    from enum import Enum
    from Event import Event
    from NaptListener import NaptListener
    from NaptRelay import NaptRelay
    from NaptConnection import NaptConnection
except Exception as ex:
    Utils.print_exception(ex)

class StdNapt(object):
    def __init__(self, bindaddr):
        self.map        = {}    # Dictionary<int, IPEndPoint>
        self.listener   = NaptListener(bindaddr);
        self.relay      = NaptRelay()

        self.istener.accepted   +=self.listener_accepted

    def __str__(self):
        return '%s { }' % self.__class__.__name__

    # public
    def start(self):
        self.listener.start()
        self.relay.start()

    # public
    def stop(self):
        self.relay.stop()
        self.listener.stop()

    # public
    def add_port(self, port, dest):
        with self.lock:
            self.map[port]  = dest
            self.listener.add_port(port)

    # public
    def remove_port(self, port):
        with self.lock:
            self.map.pop(port)
            self.listener.remove_port(port);

    # private
    def do_connect(self, e):
        try:
            local   = e.accepter.getsockname()
            port    = local[1]
            endpoint= None

            with self.lock:
                endpoint = self.map[port]

            if endpoint is None:
                return

            so      = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

            so.connect(endpoint)

            conn    = NaptConnection(e.accepted, so);

            self.relay.add_connection(conn)
        except Exception as ex:
            Utils.print_exception(ex)

    # private
    def listener_accepted(self, sender, e):  # NaptListenerEventArgs
        threading.Thread(target = self.do_connect, args = (e,), name = self.__class__.__name__).start()

