#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import struct
from enum import Enum
#from threading import Lock
from Utils  import DebugLock as Lock
from Utils import Utils

try:
    from Event import Event
    from SocketSelector import SocketSelector
    from NaptListener import NaptListenerStatus
    from NaptListenerPart import NaptListenerPart
    from NaptListenerEventArgs import NaptListenerEventArgs
except Exception as ex:
    Utils.print_exception(ex)

class NaptListener2(object):
    def __init__(self, bindaddr):
        super().__init__()

        self.lock       = Lock()
        self.bindaddr   = bindaddr
        self.status     = NaptListenerStatus.Stopped
        self.ports      = {}
        self.parts      = []
        self.port_unit  = 500 if Utils.is_windows(os.name) else 1000
        self.num_ports  = 0

        self.accepted   = Event('NaptListenerEventArgs')

    def __str__(self):
        return 'NaptListener2{ %s }' %', '.join([
            'bindaddr=%s'       % str(self.bindaddr)])

    # public
    def start(self):
        with self.lock:
            self.status     = NaptListenerStatus.Starting

            for i in self.parts:
                i.start()

            self.status     = NaptListenerStatus.Running

    def stop(self):
        with self.lock:
            self.status     = NaptListenerStatus.Stopping

            for i in self.parts:
                i.stop()

            self.status     = NaptListenerStatus.Stopped

    # public
    def add_port(self, port):
        with self.lock:
            if port in self.ports:
                raise Exception()   # ArgumentException(nameof(port))

            self.ports[port] = port
            self.num_ports   +=1

            if (self.num_ports % self.port_unit) == 1:
                part = self.add_part()

                #print('  add new part: num_ports=%d' % (self.num_ports))
            else:
                part = self.parts[-1]

            part.add_port(port)

    # public
    def remove_port(self, port):
        with self.lock:
            for i in self.parts:
                i.remove_port(port)

    # private
    def add_part(self):
        Utils.assertion(self.lock.locked(), 'need lock')

        part = NaptListenerPart(self.bindaddr)

        part.accepted += self.part_accepted

        self.parts.append(part)

        return part

    # private
    def part_accepted(self, sender, e):
        self.on_accepted(e)

    # protected virtual
    def on_accepted(self, e):   # NaptListenerEventArgs
        self.accepted(self, e)
