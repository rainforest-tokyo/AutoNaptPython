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
import struct
import threading
from collections import deque
from enum import Enum
from threading import Lock
from Utils import Utils

try:
    from Event import Event
except Exception as ex:
    Utils.print_exception(ex)

class NaptSocket(object):
    def __init__(self, owner, so, client):
        Utils.expects_type(socket.socket, so, 'so', True)

        self.lock           = Lock()
        self.owner          = owner
        self.socket         = so
        self.is_client      = client
        self.is_sending     = False
        self.status         = NaptSocketStatus.Disconnected if so is None else NaptSocketStatus.Connected
        self.send_buffers   = deque()
        self.tag            = None
        self.debug          = False

        if self.socket is None:
            self.peername   = None
            self.sockname   = None
        else:
            self.peername   = self.socket.getpeername()
            self.sockname   = self.socket.getsockname()

    def __str__(self):
        if self.socket is None:
            return 'NaptSocket { %s }' %', '.join([
                'status=%s'     % str(self.status),
                'is_client=%s'  % str(self.is_client)])
        else:
            return 'NaptSocket { %s }' %', '.join([
                'status=%s'     % str(self.status),
                'is_client=%s'  % str(self.is_client),
                'peer=%s'       % str(self.peername),
                'sock=%s'       % str(self.sockname) ])

    # internal
    def connect(self, endpoint):
        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

        so.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 0, 0))
        so.connect(endpoint)

        # バッファにデータがある場合は、送信処理を開始する
        with self.lock:
            self.socket     = so
            self.peername   = self.socket.getpeername()
            self.sockname   = self.socket.getsockname()

            if self.status != NaptSocketStatus.Connecting:
                self.do_close()
                return

            self.status     = NaptSocketStatus.Connected

            if len(self.send_buffers) != 0:
                self.start_send()

    # internal
    def close(self):
        if self.debug:
            print('  NaptSocket.close: %s' % str(self))

        with self.lock:
            if self.status == NaptSocketStatus.Connected:
                self.do_close()
                return True
            else:
                self.status = NaptSocketStatus.Closed
                return False

    # private
    def do_close(self):
        #Utils.assertion(self.lock.locked(), 'need lock')

        self.status = NaptSocketStatus.Closed

        self.socket.close() # non-blocking

    # internal
    def push(self, data, offset, size):
        with self.lock:
            self.send_buffers.append(data[offset:offset+size])  # Enqueue

            # non connected
            if self.status != NaptSocketStatus.Connected:
                return

            if not self.is_sending:
                self.start_send()

    # private
    def start_send(self):
        Utils.assertion(self.lock.locked(), 'need lock')

        self.is_sending   = True

        threading.Thread(target = self.do_send, name = self.__class__.__name__).start()

    # private
    def do_send(self):
        while True:
            data = None

            with self.lock:
                if len(self.send_buffers) == 0:
                    self.is_sending   = False
                    return

                data= self.send_buffers.popleft()   # Dequeue

            try:
                #self.socket.settimeout(5.0)
                self.socket.sendall(data)
            except Exception as ex:
                Utils.print_exception(ex)
                self.do_close()
                    
class NaptSocketStatus(Enum):
    Disconnected= 1
    Connecting  = 2
    Connected   = 3
    Closed      = 4
