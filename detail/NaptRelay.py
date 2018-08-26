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
from enum import Enum
from threading import Lock
from Utils import Utils

try:
    from SocketSelector import SocketSelector
    from SocketPoller import SocketPoller, SocketPollFlag
except Exception as ex:
    Utils.print_exception(ex)

class NaptRelay(object):
    def __init__(self):
        super().__init__()

        self.lock       = Lock()
        self.sockets    = {}    # Dictionary<Socket, NaptSocket>
        self.status     = NaptRelayStatus.Stopped
        self.debug      = False

    def __str__(self):
        return 'NaptRelay { %s }' %', '.join([
            'status=%s'  % str(self.statu )])

    # public
    def add_connection(self, conn):
        # todo 1024を超えるソケットを扱う場合
        with self.lock:
            with conn.lock:
                if self.debug:
                    print('add_connection(%s)' % str(conn), flush=True)

                if conn.client is not None and conn.client.socket is not None:
                    self.sockets[conn.client.socket]= conn.client

                    self.register_poll(conn.client.socket)

                if conn.server is not None and conn.server.socket is not None:
                    self.sockets[conn.server.socket]= conn.server

                    self.register_poll(conn.server.socket)

                conn.connected      +=self.conn_connected
                conn.closed         +=self.conn_closed
                conn.client_closing +=self.conn_client_closing
                conn.server_closing +=self.conn_server_closing
                conn.client_closed  +=self.conn_client_closed
                conn.server_closed  +=self.conn_server_closed

                if self.debug:
                    print('add_connection(%s) done' % str(conn), flush=True)

    def register_poll(self, so):
        SocketPoller.get_instance().register(so, SocketPollFlag.ReadError, self.polling_callback)

    def unregister_poll(self, so):
        SocketPoller.get_instance().unregister(so)

    # private
    def conn_connected(self, sender, e):
        conn= sender;

        with self.lock:
            with conn.lock:
                if not conn.server is None and not conn.server.socket is None:
                    self.sockets[conn.server.socket]= conn.server

                    self.register_poll(conn.server.socket)

                    if self.debug:
                        print('  add_socket(server: %s' % str(conn.server))

    # private
    def conn_closed(self, sender, e):
        conn= sender;

    # private
    def conn_client_closed(self, sender, e):
        conn= sender;

        with self.lock:
            Utils.assertion(conn.client.socket is not None,     'socket is None')
            Utils.assertion(conn.client.socket in self.sockets, 'socket not found')

            self.sockets.pop(conn.client.socket)

            if self.debug:
                print('  remove_socket(client: %s' % str(conn.client))

    # private
    def conn_server_closed(self, sender, e):
        conn= sender;

        with self.lock:
            Utils.assertion(conn.server.socket is not None,     'socket is None')
            Utils.assertion(conn.server.socket in self.sockets, 'socket not found')

            self.sockets.pop(conn.server.socket)

            if self.debug:
                print('  remove_socket(server: %s' % str(conn.server))

    # private
    def conn_client_closing(self, sender, e):
        conn    = sender

        if conn.client.socket is not None:
            self.unregister_poll(conn.client.socket)

    # private
    def conn_server_closing(self, sender, e):
        conn    = sender

        if conn.server.socket is not None:
            self.unregister_poll(conn.server.socket)

    def polling_callback(self, so, flag):
        if bool(flag & SocketPollFlag.Read):
            self.do_recv(so)

        if bool(flag & SocketPollFlag.Write):
            self.do_send(so)

        if bool(flag & SocketPollFlag.Error):
            self.do_error(so)

    # protected override
    def do_recv(self, so):
        Utils.expects_type(socket.socket, so, 'so')

        naptso = None

        with self.lock:
            naptso = self.sockets[so]

        if naptso is not None:
            naptso.owner.recv(naptso)
        else:
            print('warning: NaptSocket is not found')

    # protected override
    def do_send(self, so):
        Utils.expects_type(socket.socket, so, 'so')

        pass

    # protected override
    def do_error(self, so):
        Utils.expects_type(socket.socket, so, 'so')

        nso = None

        try:
            with self.lock:
                nso = self.sockets[so]

            if nso is not None:
                nso.owner.error(nso)
        except Exception:
            pass # とりあえずなにもしない

class NaptRelayStatus(Enum):
    Stopped     = 1
    Starting    = 2
    Running     = 3
    Stopping    = 4
