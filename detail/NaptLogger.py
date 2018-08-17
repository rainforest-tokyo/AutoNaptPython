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
import datetime
import json
import hashlib
from threading import Lock
from Utils import Utils

from ElasticConnector import ElasticConnector
import geoip2.database

try:
    from NaptConnection import NaptConnection
except Exception as ex:
    Utils.print_exception(ex)

class NaptLogger(object):
    def __init__(self, file, elastic):
        self.lock       = Lock()
        self.file       = file
        if(elastic == True) :
            self.elastic    = ElasticConnector()
        #self.packet_dir = None
        #self.save_packet= False

        self.geoip_city_reader = geoip2.database.Reader(os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), 'geoip/GeoLite2-City.mmdb'))
        self.geoip_asn_reader = geoip2.database.Reader(os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), 'geoip/GeoLite2-ASN.mmdb'))

    def city_info(self, ip):
        response = self.geoip_city_reader.city(ip)
        return {
            "iso_code": response.country.iso_code,
            "name": response.country.name,
            "divisions": response.subdivisions.most_specific.name,
            "postal_code": response.postal.code,
            "location": {
                "lat": response.location.latitude,
                "lon": response.location.longitude
            }
        }


    def asn_info(self, ip):
        response = self.geoip_asn_reader.asn( ip )
        return {
            "asn" : response.autonomous_system_organization
        }

    def log_accepted(self, conn):
        Utils.expects_type(NaptConnection, conn, 'conn')

        log     = None

        with conn.lock:
            remote  = conn.client.peername
            local   = conn.client.sockname
            log     = self.create_log(conn.id, 'accept', {
                'client': {
                    'remote':   { 'address': remote[0], 'port': remote[1], 
                        'geoip': { 'city': self.city_info(remote[0]), 'asn': self.asn_info(remote[0])}
                    },
                    'local':    { 'address': local[0],  'port': local[1] }
            } })

        self.append_log(log)

        if( self.elastic != None ) :
            self.elastic.store( log )

    def log_connected(self, conn):
        Utils.expects_type(NaptConnection, conn, 'conn')

        log     = None

        with conn.lock:
            status  = conn.tag
            protocol= status.protocol_setting
            c_remote= conn.client.socket.getpeername()
            c_local = conn.client.socket.getsockname()
            s_remote= conn.server.socket.getpeername()
            s_local = conn.server.socket.getsockname()
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

        if( self.elastic != None ) :
            self.elastic.store( log )

    def log_close(self, conn):
        Utils.expects_type(NaptConnection, conn, 'conn')

        log     = None

        with conn.lock:
            log     = self.create_log(conn.id, 'close')

        self.append_log(log)

    def log_recv(self, conn, data, offset, size):
        Utils.expects_type(NaptConnection, conn, 'conn')

        size2   = size
        size2   = 256 if size2 > 256 else size2
        log     = None
        store_data   = data[0:size2]

        protocol= ''
        try :
            status  = conn.tag
            protocol= status.protocol_setting
        except :
            pass

        with conn.lock:
            log     = self.create_log(conn.id, 'recv', {
                'packet_size':      size,
                'packet':           Utils.get_string_from_bytes(store_data, 'charmap'),
                'sha1':             hashlib.sha1(store_data).hexdigest()
                #'packet':           Utils.get_string_from_bytes(data[0:size2], 'ascii')
                #'packet':           Utils.get_escaped_string(data[0:size2])
            })

        if( (self.elastic != None) and ('HTTP' in protocol) ) :
            self.append_log(log)
            self.elastic.store( log )

    def log_send(self, conn, data, offset, size):
        Utils.expects_type(NaptConnection, conn, 'conn')

        size2   = size
        size2   = 256 if size2 > 256 else size2
        log     = None
        store_data   = data[0:size2]

        with conn.lock:
            log     = self.create_log(conn.id, 'send', {
                'packet_size':      size,
                'packet':           Utils.get_string_from_bytes(store_data, 'charmap'),
                'sha1':             hashlib.sha1(store_data).hexdigest()
                #'packet':           Utils.get_string_from_bytes(data[0:size2], 'ascii')
                #'packet':           Utils.get_escaped_string(data[0:size2])
            })

        # AWSのDiskが圧迫するので一旦コメントアウト
        #self.append_log(log)

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
