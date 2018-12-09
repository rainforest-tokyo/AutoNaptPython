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
import threading
from threading import Lock
from Utils import Utils

try:
    from Event import Event
    from NaptSocket import NaptSocket, NaptSocketStatus
    from NaptConnectionEventArgs import NaptConnectionEventArgs
except Exception as ex:
    Utils.print_exception(ex)

class NaptConnection(object):
    def __init__(self, client, server):
        Utils.expects_type(socket.socket, client, 'client')
        Utils.expects_type(socket.socket, server, 'server', True)

        self.lock           = Lock()
        self.id             = 0
        self.client         = NaptSocket(self, client, True)
        self.server         = NaptSocket(self, server, False)
        self.is_connecting  = False
        self.is_connected   = False
        self.is_closed      = False
        self.tag            = None
        self.tls            = False
        self.debug          = True
        self.bind_port      = 0

        self.connected      = Event()
        self.closed         = Event()
        self.client_closing = Event()
        self.server_closing = Event()
        self.client_closed  = Event()
        self.server_closed  = Event()
        self.client_recieved= Event()
        self.server_recieved= Event()

    def __str__(self):
        return 'NaptConnection{ %s }' % ', '.join([
            'id=%d'             % self.id,
            'client=%s'         % str(self.client),
            'server=%s'         % str(self.server),
            'is_connecting=%s'  % str(self.is_connecting),
            'is_connected=%s'   % str(self.is_connected)])

    # public
    def connect(self, endpoint):
        Utils.assertion(self.lock.locked(), 'need lock')

        if self.is_connecting:
            raise Exception() # InvalidOperationException

        self.is_connecting  = True
        self.server.status  = NaptSocketStatus.Connecting

        threading.Thread(target = self.do_connect, args = (endpoint,), name = self.__class__.__name__).start()

    # private
    def do_connect(self, endpoint):
        try:
            self.server.connect(endpoint)   # blocking

            #self.client.socket.settimeout(5.0)
            #self.server.socket.settimeout(5.0)

            with self.lock:
                if self.is_closed:
                    # todo close
                    return

                self.is_connected = True

            #print('INVOKE: on_connected')

            self.on_connected(None)
        except Exception as ex:
            print('  endpoint: %s' % str(endpoint))
            Utils.print_exception(ex)
            self.close()

    # public
    def close(self):
        with self.lock:
            #if self.is_closed:
            #    return

            self.close_client()
            self.close_server()
            self.is_closed    = True

        if self.debug:
            print('NaptConnection.close: %s' % str(self))

        self.on_closed(None)

    # protected virtual
    def on_connected(self, e):
        self.connected(self, e)

    # protected virtual
    def on_closed(self, e):
        self.closed(self, e)

    # protected virtual
    def on_client_closing(self, e):
        self.client_closing(self, e)

    # protected virtual
    def on_server_closing(self, e):
        self.server_closing(self, e)

    # protected virtual
    def on_client_closed(self, e):
        self.client_closed(self, e)

    # protected virtual
    def on_server_closed(self, e):
        self.server_closed(self, e)

    # protected virtual
    def on_client_recieved(self, e):    # NaptConnectionEventArgs 
        self.client_recieved(self, e)

    # protected virtual
    def on_server_recieved(self, e):    # NaptConnectionEventArgs 
        self.server_recieved(self, e)

    # internal
    def recv(self, so):
        Utils.expects_type(NaptSocket, so, 'so')

        if so.is_client:
            self.recv_client()
        else:
            self.recv_server()

    # internal
    def error(self, so):
        Utils.expects_type(NaptSocket, so, 'so')

        # todo error

    # private
    def recv_client(self):
        try:
            #self.client.socket.settimeout(5.0)
            #self.server.socket.settimeout(5.0)
            data= self.client.socket.recv(4096)
            e   = NaptConnectionEventArgs(self, data, 0, len(data))

            if len(data) == 0:  # closed
                #self.close_client();
                self.close()
                return

            #print('    DATA: %s' % str(data), flush=True)

            self.on_client_recieved(e)
            self.server.push(data, 0, len(data))
        except Exception as ex: # SocketException
            Utils.print_exception(ex)
            self.close()

    # private
    def recv_server(self):
        try:
            #self.client.socket.settimeout(5.0)
            #self.server.socket.settimeout(5.0)
            data= self.server.socket.recv(4096)
            e   = NaptConnectionEventArgs(self, data, 0, len(data))

            if len(data) == 0:  # closed
                #self.close_server()
                self.close()
                return

            #print('    DATA: %s' % str(data), flush=True)

            self.on_server_recieved(e)
            self.client.push(data, 0, len(data))
        except Exception as ex: # SocketException
            Utils.print_exception(ex)
            self.close()

    # private
    def close_client(self):
        #if self.debug:
        #    print('  NaptConnection.close_client: %s' % str(self.client))

        try:
            self.on_client_closing(None)
        except Exception as ex:
            Utils.print_exception(ex)

        try:
            if self.client.close():
                self.on_client_closed(None)
        except Exception as ex:
            Utils.print_exception(ex)

    # private void
    def close_server(self):
        #if self.debug:
        #    print('  NaptConnection.close_server: %s' % str(self.server))

        try:
            self.on_server_closing(None)
        except Exception as ex:
            Utils.print_exception(ex)

        try:
            if self.server.close():
                self.on_server_closed(None);
        except Exception as ex:
            Utils.print_exception(ex)
