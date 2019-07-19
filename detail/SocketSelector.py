#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import select
import threading
import time
#from threading import Lock
from Utils  import DebugLock as Lock
from Utils import Utils

try:
    from Event import Event
except Exception as ex:
    Utils.print_exception(ex)

class SocketSelector(object):
    def __init__(self):
        if Utils.is_linux(os.name):
            self.impl = SocketSelectorLinux(self)
        else:
            self.impl = SocketSelectorOther(self)

        self.lock           = Lock()
        self.read_sockets   = []    # List<Socket>
        self.write_sockets  = []    # List<Socket>
        self.error_sockets  = []    # List<Socket>
        self.timeout        = 1.0
        self.thread         = None
        self.running        = False

        self.started        = Event('EventArgs')
        self.stopped        = Event('EventArgs')

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
            self.do_select()

        self.on_stopped(None)

        with self.lock:
            self.thread = None

    # protected virtual
    def do_select(self):
        self.impl.do_select()

    # protected virtual
    def do_recv(self, so):
        pass

    # protected virtual
    def do_send(self, so):
        pass

    # protected virtual
    def do_error(self, so):
        pass

class SocketSelectorLinux(object):
    def __init__(self, owner):
        self.owner      = owner
        self.poller     = select.poll()
        self.registered = {}
        self.fd_map     = {}

    # protected virtual
    def do_select(self):
        empty   = True
        owner   = self.owner

        with owner.lock:
            owner.read_sockets.clear()
            owner.write_sockets.clear()
            owner.error_sockets.clear()
            owner.update_select_sockets()

            empty   = len(owner.read_sockets) == 0 \
                  and len(owner.write_sockets) == 0 \
                  and len(owner.error_sockets) == 0

            if not empty:
                self.restruct_poll()

        try:
            if(empty):
                time.sleep(owner.timeout)
                return

            events = self.poller.poll(owner.timeout)

            for fd, ev in events:
                so = self.fd_map[fd]

                if ev & select.POLLIN:
                    owner.do_recv(so)

                if ev & select.POLLOUT:
                    owner.do_send(so)

                if ev & select.POLLERR:
                    owner.do_error(so)
        except Exception as ex:
            # ThreadInterruptedException
            # Exception
            Utils.print_exception(ex)


    # protected virtual
    def restruct_poll(self):
        flags       = {}
        self.fd_map = {}

        for so in self.owner.read_sockets:
            flags[so] = (flags[so] or select.POLLIN)  if so in flags else select.POLLIN

        for so in self.owner.write_sockets:
            flags[so] = (flags[so] or select.POLLOUT) if so in flags else select.POLLOUT

        for so in self.owner.error_sockets:
            flags[so] = (flags[so] or select.POLLERR) if so in flags else select.POLLERR

        for so, flag in flags.items():
            self.fd_map[so.fileno()] = so

            if so in self.registered:
                self.poller.modify(so, flag | select.POLLPRI | select.POLLHUP)
            else:
                self.poller.register(so, flag | select.POLLPRI | select.POLLHUP)
                self.registered[so] = True

        for so in self.registered.keys():
            if not so in flags:
                self.poller.unregister(so)
                self.registered.pop(so)

class SocketSelectorOther(object):
    def __init__(self, owner):
        self.owner = owner

    # protected virtual
    def do_select(self):
        empty   = True
        owner   = self.owner

        with owner.lock:
            owner.read_sockets.clear()
            owner.write_sockets.clear()
            owner.error_sockets.clear()
            owner.update_select_sockets()

            empty   = len(owner.read_sockets) == 0 \
                  and len(owner.write_sockets) == 0 \
                  and len(owner.error_sockets) == 0

        try:
            if(empty):
                time.sleep(owner.timeout)
                return

            read, write, error = select.select(owner.read_sockets, owner.write_sockets, owner.error_sockets, owner.timeout)

            for i in read:
                owner.do_recv(i)

            for i in write:
                owner.do_send(i)

            for i in error:
                owner.do_error(i)
        except Exception as ex:
            # ThreadInterruptedException
            # Exception
            Utils.print_exception(ex)
