#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import struct
from enum import Enum
from Utils import Utils

try:
    from Event import Event
    from SocketSelector import SocketSelector
    from NaptListener import NaptListenerStatus
    from NaptListenerEventArgs import NaptListenerEventArgs
except Exception as ex:
    Utils.print_exception(ex)

class NaptListenerPart(SocketSelector):
    def __init__(self, bindaddr):
        super().__init__()

        self.bindaddr   = bindaddr
        self.sockets    = {}    # Dictionary<int, Socket>
        self.status     = NaptListenerStatus.Stopped

        self.accepted   = Event('NaptListenerEventArgs')

    def __str__(self):
        return 'NaptListener{ %s }' %', '.join([
            'bindaddr=%s'       % str(self.bindaddr)])

    # protected override
    def do_start(self):
        if self.status != NaptListenerStatus.Stopped:
            raise Exception()   # InvalidOperationException
            
        super().do_start()

        self.status     = NaptListenerStatus.Starting

    # protected override
    def do_stop(self):
        if self.status != NaptListenerStatus.Running:
            raise Exception()   # InvalidOperationException

        super().do_stop()

        self.status     = NaptListenerStatus.Stopping

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

        print('  %s' % str(endpoint))

        so.bind(endpoint)
        so.listen(10)

        self.sockets[port]  = so

        if self.thread is not None:
            pass
            #signal.alarm(3)    # Thread.Interrupt()

    # public
    def remove_port(self, port):
        with self.lock:
            so = self.sockets[port]

            if so is None:
                return

            self.sockets.pop(port)

            so.close()

            if self.thread is not None:
                pass
                #signal.alarm(3)    # Thread.Interrupt()


    # protected virtual
    def on_accepted(self, e):   # NaptListenerEventArgs
        self.accepted(self, e)

    # protected override
    def run(self):
        with self.lock:
            self.status  = NaptListenerStatus.Running

        super().run();

        with self.lock:
            self.status  = NaptListenerStatus.Stopped

    # protected override
    def do_recv(self, so):
        Utils.expects_type(socket.socket, so, 'so')

        try:
            accepted, remote= so.accept();

            accepted.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 0, 0))

            #################
            # Add Okada
            accepted.settimeout(15.0)
            #################

            e       = NaptListenerEventArgs(accepted, so);

            self.on_accepted(e)
        except Exception as ex:
            Utils.print_exception(ex)

            raise ex

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
