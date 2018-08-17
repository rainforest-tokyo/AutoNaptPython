#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import select
import threading
import time
from threading import Lock
from enum import Flag
from Utils import Utils

try:
    from Event import Event
except Exception as ex:
    Utils.print_exception(ex)

# abstract
class SocketPoller(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = SocketPollerLinux() if Utils.is_linux(os.name) else SocketPollerOther()

        return cls._instance

    def __init__(self):
        self.lock           = Lock()
        self.descripters    = {}
        self.fd_map         = {}
        self.timeout        = 1.0
        self.thread         = None
        self.running        = False
        self.debug          = False

        self.started        = Event('EventArgs')
        self.stopped        = Event('EventArgs')
        self.idle           = Event('EventArgs')

    # public
    def register(self, fd, flags, callback):
        #print('register:   %d' % fd.fileno())

        with self.lock:
            self.do_register(fd, flags, callback)

    # public
    def unregister(self, fd):
        #print('unregister: %d' % fd.fileno())

        with self.lock:
            self.do_unregister(fd)

    # protected virtual
    def on_idle(self, e):
        self.idle(self, e)

    # protected virtual
    def do_register(self, fd, flag, callback):
        self.descripters[fd]    = (flag, callback)
        self.fd_map[fd.fileno()]= fd

    # protected virtual
    def do_unregister(self, fd):
        self.descripters.pop(fd)
        self.fd_map.pop(fd.fileno())

    # public
    def start(self):
        with self.lock:
            self.do_start();

    # public
    def stop(self):
        with self.lock:
            self.do_stop();

    # protected abstract
    def update_select_sockets(self):
        pass

    # protected virtual
    def on_started(self, e):
        self.started(self, e)   # fire event

    # protected virtual
    def on_stopped(self, e):
        self.stopped(self, e)   # fire event

    # protected virtual
    def do_start(self):
        Utils.assertion(self.lock.locked(), 'need lock')

        if self.thread is not None:
            raise Exception()   # InvalidOperationException()

        self.thread = threading.Thread(target = self.run, name = self.__class__.__name__)
        self.running= True

        self.thread.start()

    # protected virtual
    def do_stop(self):
        Utils.assertion(self.lock.locked(), 'need lock')

        if self.thread is None:
            raise Exception()   # InvalidOperationException()

        self.running= False

    # protected virtual
    def run(self):
        self.on_started(None)

        while(self.running):
            try :
                self.do_poll()
                self.on_idle(None)
            except :
                pass

        self.on_stopped(None)

        with self.lock:
            self.thread = None

    def do_poll(self):
        raise Exception('not implemented')
        pass

    def invoke_callback(self, fd, flag):
        callback = None
        with self.lock:
            if fd not in self.descripters:
                return

            flag2, callback = self.descripters[fd]

        if callback is not None:
            callback(fd, flag)

class SocketPollerOther(SocketPoller):
    def __init__(self):
        super().__init__()

        self.lock           = Lock()
        self.read_sockets   = {}    # Dictionary<Socket, bool>
        self.write_sockets  = {}    # Dictionary<Socket, bool
        self.error_sockets  = {}    # Dictionary<Socket, bool>

    # protected virtual
    def do_register(self, fd, flag, callback):
        super().do_register(fd, flag, callback)

        if bool(flag & SocketPollFlag.Read):
            self.read_sockets[fd]   = True

        if bool(flag & SocketPollFlag.Write):
            self.write_sockets[fd]  = True

        if bool(flag & SocketPollFlag.Error):
            self.error_sockets[fd]  = True

    # protected virtual
    def do_unregister(self, fd):
        super().do_unregister(fd)

        fd in self.read_sockets  and self.read_sockets.pop(fd)
        fd in self.write_sockets and self.write_sockets.pop(fd)
        fd in self.error_sockets and self.error_sockets.pop(fd)

    def do_poll(self):
        empty       = True
        try_read    = None
        try_write   = None
        try_error   = None

        with self.lock:
            empty   = len(self.read_sockets)  == 0 \
                  and len(self.write_sockets) == 0 \
                  and len(self.error_sockets) == 0

            if not empty:
                try_read    = self.read_sockets.keys()
                try_write   = self.write_sockets.keys()
                try_error   = self.error_sockets.keys()

        try:
            if(empty):
                time.sleep(self.timeout)
                return

            read, write, error = select.select(try_read, try_write, try_error, self.timeout)

            if len(read) == 0 and len(write) == 0 and len(error) == 0:
                return

            flags = {}

            for fd in read:
                flags[fd] = (flags[fd] | SocketPollFlag.Read)  if fd in flags else SocketPollFlag.Read

            for fd in write:
                flags[fd] = (flags[fd] | SocketPollFlag.Write) if fd in flags else SocketPollFlag.Write

            for fd in error:
                flags[fd] = (flags[fd] | SocketPollFlag.Error) if fd in flags else SocketPollFlag.Error

            for fd, flag in flags.items():
                self.invoke_callback(fd, flag)
        except Exception as ex:
            # ThreadInterruptedException
            # Exception
            Utils.print_exception(ex)

            self.running = False

class SocketPollerLinux(SocketPoller):
    def __init__(self):
        super().__init__()

        self.lock           = Lock()
        self.poller         = select.epoll()

    # protected virtual
    def do_register(self, fd, flag, callback):
        super().do_register(fd, flag, callback)

        pollflag    = (select.EPOLLIN  if bool(flag & SocketPollFlag.Read)  else 0) \
                    | (select.EPOLLOUT if bool(flag & SocketPollFlag.Write) else 0) \
                    | (select.EPOLLERR if bool(flag & SocketPollFlag.Error) else 0)

        #print('register: %d:%X %d' % (fd.fileno(), pollflag, len(self.descripters)), flush=True)

        self.poller.register(fd, pollflag)

    # protected virtual
    def do_unregister(self, fd):
        super().do_unregister(fd)

        self.poller.unregister(fd)

    def do_poll(self):
        empty       = True

        with self.lock:
            empty = len(self.descripters) == 0

        try:
            if(empty):
                time.sleep(self.timeout)
                return

            status = self.poller.poll(self.timeout)

            for fd, pollflag in status:
                flag    = (SocketPollFlag.Read  if bool(pollflag & select.EPOLLIN)  else SocketPollFlag.Zero) \
                        | (SocketPollFlag.Write if bool(pollflag & select.EPOLLOUT) else SocketPollFlag.Zero) \
                        | (SocketPollFlag.Error if bool(pollflag & select.EPOLLERR) else SocketPollFlag.Zero)

                #print('  signaled fd: %d' % fd, flush=True)

                fd_obj = self.fd_map[fd]

                self.invoke_callback(fd_obj, flag)
        except Exception as ex:
            # ThreadInterruptedException
            # Exception
            Utils.print_exception(ex)

            self.running = False
                        
class SocketPollFlag(Flag):
    Zero        = 0
    Read        = 1
    Write       = 2
    ReadWrite   = 3
    Error       = 4
    ReadError   = 5
    WriteError  = 6
    All         = 7
