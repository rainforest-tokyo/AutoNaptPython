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
import select
import struct
from enum import Enum
from threading import Lock
from Utils import Utils

try:
    from Event2 import Event2
    from SocketSelector import SocketSelector
    from SocketPoller import SocketPoller, SocketPollFlag
    from NaptListenerEventArgs import NaptListenerEventArgs
except Exception as ex:
    Utils.print_exception(ex)

class NaptListener(object):
    def __init__(self, bindaddr):
        super().__init__()

        self.lock       = Lock()
        self.bindaddr   = bindaddr
        self.sockets    = {}    # Dictionary<int, Socket>
        self.status     = NaptListenerStatus.Stopped
        self.port       = 0 

        self.accepted   = Event2('NaptListenerEventArgs')

    def __str__(self):
        return 'NaptListener{ %s }' %', '.join([
            'bindaddr=%s'       % str(self.bindaddr)])

    # public
    def add_port(self, port):
        with self.lock:
            if port in self.sockets:
                raise Exception()   # ArgumentException(nameof(port))

            self.listen(port)

    # private
    def listen(self, port):
        # todo ここでBindしないでStart時のBind,Stop時にCloseする
        so      = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        bindaddr= '0.0.0.0' if self.bindaddr == 'any' else self.bindaddr
        endpoint= (bindaddr, port)
        self.port       = port 

        print('  %s' % str(endpoint))

        so.bind(endpoint)
        so.listen(10)

        SocketPoller.get_instance().register(so, SocketPollFlag.ReadError, self.polling_callback)

    # public
    def remove_port(self, port):
        with self.lock:
            so = self.sockets[port]

            SocketPoller.get_instance().unregister(so)

            self.sockets.pop(port)

            so.close()

    # protected virtual
    def on_accepted(self, e):   # NaptListenerEventArgs
        self.accepted(self, e)

    # private
    def polling_callback(self, so, flag):
        if 0 != (flag & SocketPollFlag.Read):
            self.do_recv(so)

        if 0 != (flag & SocketPollFlag.Write):
            self.do_send(so)

        if 0 != (flag & SocketPollFlag.Error):
            self.do_error(so)

    # protected override
    def do_recv(self, so):
        Utils.expects_type(socket.socket, so, 'so')

        try:
            so.settimeout(3.0)
            so_accepted, remote= so.accept();

            so_accepted.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 0, 0))

            e       = NaptListenerEventArgs(so_accepted, so, self.port);

            self.on_accepted(e)
        except Exception as ex:
            print('do_recv: Exception', flush=True)
            Utils.print_exception(ex)
            print('', flush=True)
            try:
                key = [k for k, v in self.sockets.items() if v == so][0]
                self.remove_port(key)
            except Exception as ex:
                pass
            #raise ex

    # protected override
    def do_send(self, so):
        Utils.expects_type(socket.socket, so, 'so')

    # protected override
    def do_error(self, so):
        Utils.expects_type(socket.socket, so, 'so')

        # todo error

    # protected override
    def update_select_sockets(self):
        Utils.assertion(self.lock.locked(), 'need lock')

        self.read_sockets.extend(self.sockets.values())
        self.error_sockets.extend(self.sockets.values())

class NaptListenerStatus(Enum):
    Stopped     = 1
    Starting    = 2
    Running     = 3
    Stopping    = 4
