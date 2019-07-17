#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import json
#from threading import Lock
from Utils  import DebugLock as Lock
from Utils import Utils

try:
    from NaptConnection import NaptConnection
except Exception as ex:
    Utils.print_exception(ex)

class NaptLogger(object):
    def __init__(self, file):
        self.lock       = Lock()
        self.file       = file
        #self.packet_dir = None
        #self.save_packet= False

    def log_accepted(self, conn):
        Utils.expects_type(NaptConnection, conn, 'conn')

        log     = None

        with conn.lock:
            remote  = conn.client.peername
            local   = conn.client.sockname
            log     = self.create_log(conn.id, 'accept', {
                'client': {
                    'remote':   { 'address': remote[0], 'port': remote[1] },
                    'local':    { 'address': local[0],  'port': local[1] }
            } })

        self.append_log(log)

    def log_connected(self, conn):
        Utils.expects_type(NaptConnection, conn, 'conn')

        log     = None

        with conn.lock:
            status  = conn.tag
            protocol= status.protocol_setting
            c_remote= conn.client.peername
            c_local = conn.client.sockname
            s_remote= conn.server.peername
            s_local = conn.server.sockname
            log     = self.create_log(conn.id, 'connect', {
                'protocol': protocol.name,
                'client': {
                    'remote':   { 'address': c_remote[0], 'port': c_remote[1] },
                    'local':    { 'address': c_local[0],  'port': c_local[1] },
                },
                'server': {
                    'remote':   { 'address': s_remote[0], 'port': s_remote[1] },
                    'local':    { 'address': s_local[0],  'port': s_local[1] }
                }
            })

        self.append_log(log)

    def log_close(self, conn):
        Utils.expects_type(NaptConnection, conn, 'conn')

        log     = None

        with conn.lock:
            log     = self.create_log(conn.id, 'close')

        self.append_log(log)

    def log_recv(self, conn, data, offset, size):
        Utils.expects_type(NaptConnection, conn, 'conn')

        size2   = size
        #size2   = 256 if size2 > 256 else size2
        log     = None

        with conn.lock:
            log     = self.create_log(conn.id, 'recv', {
                'packet_size':      size,
                'packet':           Utils.get_string_from_bytes(data[0:size2], 'charmap')
                #'packet':           Utils.get_string_from_bytes(data[0:size2], 'ascii')
                #'packet':           Utils.get_escaped_string(data[0:size2])
            })

        self.append_log(log)

    def log_send(self, conn, data, offset, size):
        Utils.expects_type(NaptConnection, conn, 'conn')

        size2   = size
        #size2   = 256 if size2 > 256 else size2
        log     = None

        with conn.lock:
            log     = self.create_log(conn.id, 'send', {
                'packet_size':      size,
                'packet':           Utils.get_string_from_bytes(data[0:size2], 'charmap')
                #'packet':           Utils.get_string_from_bytes(data[0:size2], 'ascii')
                #'packet':           Utils.get_escaped_string(data[0:size2])
            })

        self.append_log(log)

    def append_line(self, line):            
        with self.lock:
            with open(self.file, 'a') as f:
                f.write(line + "\n")

    def append_log(self, log):            
        line    = json.dumps(log)

        self.append_line(line)

    def create_log(self, id, type, hash = None):
        hash = {} if hash is None else hash
        hash['connection_id']   = id
        hash['datetime']        = str(datetime.datetime.now())
        hash['type']            = type

        return hash
