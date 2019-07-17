#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
from threading import Lock
from Utils import Utils

try:
    from NaptListener import NaptListener
    from NaptListener2 import NaptListener2
    from NaptRelay import NaptRelay
    from NaptConnection import NaptConnection
    from NaptLogger import NaptLogger
    from SocketPoller import SocketPoller
    from PortSetting import PortSettingList, PortSetting
    from ProtocolSetting import ProtocolSettingList, ProtocolSetting
except Exception as ex:
    Utils.print_exception(ex)

class AutoNapt(object):
    def __init__(self, bindaddr = 'any'):
        self.lock               = Lock()
        self.listener           = NaptListener(bindaddr)
        self.relay              = AutoNaptRelay(self)
        self.port_settings      = None
        self.protocol_settings  = None
        self.port_map           = {}    # Dictionary<int, PortSetting>
        self.conn_id            = 0
        self.logging            = False
        self.logger             = None
        self.debug              = True
        self.transmit_timeout   = 60    # todo from setting

        self.listener.accepted  +=self.listener_accepted

    def __str__(self):
        return '%s { }' % self.__class__.__name__

    @staticmethod
    def main(argv):
        modpath         = os.path.dirname(os.path.realpath(__file__))
        #ports           = modpath + '/../ports.json'
        #protocols       = modpath + '/../protocols.json'
        ports           = './ports.json'
        protocols       = './protocols.json'
        port_key        = 'ports'
        protocol_key    = 'protocols'
        bind            = 'any'
        logfile         = None
        transmit_timeout= 60

        i = 1

        while i < len(argv[1:]):
            if argv[i] == '--ports':
                ports       = argv[i + 1]
                i = i + 2
            elif argv[i] == '--protocols':
                protocols   = argv[i + 1]
                i = i + 2
            elif argv[i] == '--portkey':
                port_key    = argv[i + 1]
                i = i + 2
            elif argv[i] == '--protocolkey':
                protocol_key= argv[i + 1]
                i = i + 2
            elif argv[i] == '--bind':
                bind        = argv[i + 1]
                i = i + 2
            elif argv[i] == '--log':
                logfile     = argv[i + 1]
                i = i + 2
            elif argv[i] == '--timeout':
                transmit_timeout= int(argv[i + 1])
                i = i + 2
            elif argv[i] == '--help':
                return AutoNapt.usage()
            else:
                print('invalid option: %s' % argv[i])
                return AutoNapt.usage()

        napt = AutoNapt(bind)
        napt.port_settings      = PortSettingList.from_json_file(ports, port_key)
        napt.protocol_settings  = ProtocolSettingList.from_json_file(protocols, protocol_key)
        napt.transmit_timeout   = transmit_timeout

        if logfile is not None:
            napt.logger = NaptLogger(logfile)
            napt.logging= True

        napt.setup()
        napt.start()

        while True:
            try:
                #time.sleep(1)
                time.sleep(10000)
            except KeyboardInterrupt:
                break

        return 0

    @staticmethod
    def usage():
        print('python autonapt.py [--ports <port-setting.json>] [--protocols <protocol-setting.json>] [--bind <bind-ip-address>] [--log <logfile>] [--timeout <seconds>]')
        print('  --ports     : lisenするポートの設定を記述したファイルを指定 規定値は ./ports.json')
        print('  --protocols : プロトコルの判定と接続先の設定を記述したファイルを指定 規定値は ./protocol.json')
        print('  --bind      : bindをするアドレスを指定 規定値はINADDR_ANYでbindする')
        print('  --log       : ログを記録する')
        print('  --timeout   : 一定時間通信がない場合に接続を切断する')

        return 1

    #-- Operations --
    # public
    def setup(self):
        for i in self.port_settings.ports:
            print('%s' % i.name)

            for port in range(i.port_min, i.port_max+1):
                print('  port: %d' % port)

                if port in self.port_map:
                    print('Warnning: Duplicate port %d ... %s -- %s' %
                        (port, str(i), str(self.port_map[port])))
                    continue

                self.listener.add_port(port)
                self.port_map[port]= i
    
    # public
    def start(self):
        SocketPoller.get_instance().start()
        #self.relay.start()
        #self.listener.start()

    # public
    def stop(self):
        SocketPoller.get_instance().stop()
        #self.listener.stop()
        #self.relay.stop()

    #-- Event handlers --
    # private
    def listener_accepted(self, sender, e):
        conn        = NaptConnection(e.accepted, None)
        local       = e.accepter.getsockname()
        #remote      = e.accepter.getpeername()
        port        = local[1]
        port_setting= self.port_map[port]
        conn.tag    = ConnectionStatus(port_setting)

        conn.connected      +=self.conn_connected
        conn.closed         +=self.conn_closed
        conn.client_recieved+=self.conn_client_recieved
        conn.server_recieved+=self.conn_server_recieved

        with self.lock:
            conn.id     = self.conn_id
            self.conn_id+=1

        if self.debug:
            print('accepted: %d: %s' % (conn.id, str(conn)))

        if self.logging and self.logger is not None:    ### LOG ###
            self.logger.log_accepted(conn)

        self.relay.add_connection(conn)

    # private

    # private
    def conn_connected(self, sender, e):
        conn    = sender

        if self.debug:
            print('connected: %d: %s' % (conn.id, str(conn)))

        if self.logging and self.logger is not None:    ### LOG ###
            self.logger.log_connected(conn)

    # private
    def conn_closed(self, sender, e):
        conn    = sender

        if self.debug:
            print('closed: %d: %s' % (conn.id, str(conn)))

        if self.logging and self.logger is not None:    ### LOG ###
            self.logger.log_close(conn)

    # private
    def conn_client_recieved(self, sender, e):
        conn    = sender

        if self.debug:
            print('recv: %d: %s' % (conn.id, str(conn)))

        if self.logging and self.logger is not None:    ### LOG ###
            self.logger.log_recv(conn, e.data, e.offset, e.size)

        with conn.lock:
            status  = conn.tag;

            if conn.is_closed or status.connected or status.connecting:
                return

            #s       = Utils.get_string_from_bytes(e.data[e.offset:e.offset+e.size], 'ascii')
            s       = Utils.get_string_from_bytes(e.data[e.offset:e.offset+e.size], 'charmap')
            protocol= self.protocol_settings.match(s, True)

            print(str(protocol))

            # todo TLS reverse connection
            #conn.tls   = True

            self.connect(conn, protocol)

    # private
    def conn_server_recieved(self, sender, e):
        conn    = sender

        if self.debug:
            print('send: %d: %s' % (conn.id, str(conn)))

        if self.logging and self.logger is not None:    ### LOG ###
            self.logger.log_send(conn, e.data, e.offset, e.size)

    #-- Implement details --
    # internal
    def timeout(self, conn):
        Utils.expects_type(NaptConnection, conn, 'conn')

        status      = conn.tag;
        port        = status.port_setting;
        protocol    = self.protocol_settings.find(port.default_protocol)

        if conn.is_initial:
            self.connect(conn, protocol)
        else:
            conn.check_timeout()

    # private
    def connect(self, conn, protocol):
        Utils.expects_type(NaptConnection,  conn,     'conn')
        #Utils.expects_type(ProtocolSetting, protocol, 'protocol')

        try:
            status                  = conn.tag
            addr                    = protocol.address
            port                    = protocol.port
            endpoint                = (addr, port)
            conn.is_initial         = False
            status.connecting       = True
            status.protocol_setting = protocol

            conn.connect(endpoint)  # async
        except Exception as ex:
            Utils.print_exception(ex)

    def disconnect(self, conn):
        Utils.expects_type(NaptConnection,  conn,     'conn')

        try:
            #conn.close()
            conn.close2()   # connection is locked
        except Exception as ex:
            Utils.print_exception(ex)

# todo AutoNaptに統合
class AutoNaptRelay(NaptRelay):
    def __init__(self, owner):
        Utils.expects_type(AutoNapt, owner, 'owner')

        super().__init__()

        self.owner      = owner
        #self.debug_idle = True
        self.debug_idle = False

        SocketPoller.get_instance().idle += self.poller_idle

    def process_timeout(self):
        now = datetime.datetime.now()

        if self.debug_idle:
            print('%s: on_idle' % str(datetime.datetime.now()))

        # self.sockets
        sockets = self.sockets.copy()

        #for k, v in self.sockets.items():
        for k, v in sockets.items():
            conn    = v.owner

            with conn.lock:
                status  = conn.tag

                #if status.connecting or status.connected:
                #    continue
                if conn.is_initial:
                    # first payload timeout
                    delta   = (now - status.create_time).total_seconds()
                    setting = status.port_setting

                    if self.debug_idle:
                        print('  process_timeout/1: delta=%f timeout=%f'
                              % (delta, setting.timeout))

                    # timeout, first packet has not been received yet.
                    if delta >= setting.timeout:
                        self.owner.timeout(conn)
                else:
                    # recv timeout
                    delta   = (now - conn.lastrecvtime).total_seconds()

                    if self.debug_idle:
                        print('  process_timeout/2: delta=%f timeout=%f'
                              % (delta, self.owner.transmit_timeout))
                    
                    if delta >= self.owner.transmit_timeout:
                        # timeout disconnect
                        self.owner.disconnect(conn)

    def poller_idle(self, sender, e):
        self.process_timeout()

    # obsolete
    # protected override
    def update_select_sockets(self):
        #self.process_timeout()
        # todo timeout
        """
        super().update_select_sockets();

        # timeout check until first receive.
        now = datetime.datetime.now()

        for k, v in self.sockets.items():
            conn    = v.owner

            with conn.lock:
                status  = conn.tag

                if status.connecting or status.connected:
                    continue

                delta   = (now - status.create_time).total_seconds()
                setting = status.port_setting

                # timeout, first packet has not been received yet.
                if delta >= setting.timeout:
                    self.owner.timeout(conn)
        """
                    
class ConnectionStatus(object):
    def __init__(self, port_setting):
        Utils.expects_type(PortSetting, port_setting, 'port_setting')

        now                     = datetime.datetime.now()

        self.connecting         = False
        self.connected          = False
        self.port_setting       = port_setting
        self.protocol_setting   = None
        self.create_time        = now
        #self.timoput_time       = self.create_time + port_setting.timeout
        self.last_send_time     = now
        self.last_recv_time     = now
        self.last_transmit_time = now

    def update_send_time(self):
        now                     = datetime.datetime.now()

        self.last_send_time     = now
        self.last_transmit_time = now

    def update_recv_time(self):
        now                     = datetime.datetime.now()

        self.last_recv_time     = now
        self.last_transmit_time = now

    def __str__(self):
        return 'ConnectionStatus { %s }' %', '.join([
            'connecting=%s'  % str(self.connecting ),
            'connected=%s'   % str(self.connected ),
            'create_time=%s' % str(self.create_time )])
