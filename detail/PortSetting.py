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
import re
from Utils import Utils

class PortSettingList(object):
    def __init__(self):
        self.ports = []

    @staticmethod
    def from_json_file(file, keyname = 'ports'):
        data        = PortSettingList()
        obj         = Utils.load_json(file)
        #ports       = obj['ports']
        ports       = obj[keyname]
        re_port     = re.compile('^([0-9]+)-([0-9]+)$')

        for i in ports:
            item                    = PortSetting()
            item.name               = i["name"]
            item.timeout            = i["timeout"]
            item.default_protocol   = i["default_protocol"]
            item.comment            = i["comment"]
            port                    = i["port"]
            m                       = re_port.match(port)

            if m is None:
                item.port_min    = int(port)
                item.port_max    = int(port)
            else:
                item.port_min    = int(m.group(1))
                item.port_max    = int(m.group(2))

            data.ports.append(item)

        return data;

    def __str__(self):
        return '"ports": [ %s ]' % ', '.join(str(i) for i in self.ports)
        #return '[ %s ]' % ', '.join(self.ports)

class PortSetting(object):
    def __init__(self):
        self.name               = ''
        self.port_min           = 0
        self.port_max           = 0
        self.timeout            = 0.0
        self.default_protocol   = ''
        self.comment            = ''

    def __str__(self):
        port = str(self.port_min) if self.port_min == self.port_min else '%d-%d' % (self.port_min, self.port_max)

        return '{ %s }' % ', '.join([
            '"name": "%s"'              % self.name,
            '"port": "%s"'              % port,
            '"timeout": %s'             % str(self.timeout),
            '"default_protocol": "%s"'  % self.default_protocol,
            '"comment": "%s"'           % self.comment])
