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

class ProtocolSettingList(object):
    def __init__(self):
        self.protocols                  = []
        self.default_protocol           = None
        self.default_protocol_setting   = None

    # public
    def match(self, packet, use_default_when_nomatch):
        for i in self.protocols:
            for j in i.rules:
                if j.match(packet) is not None:
                    return i

        return self.default_protocol_setting if use_default_when_nomatch else None

    @staticmethod
    def from_json_file(jsonfile, keyname = 'protocols'):
        data                    = ProtocolSettingList()
        obj                     = Utils.load_json(jsonfile)
        #protocols               = obj['protocols']  # list
        protocols               = obj[keyname]      # list
        data.default_protocol   = obj['default_protocol']

        for i in protocols:
            item = ProtocolSetting()
            item.name           = i['name']
            item.address        = i['server']['address']
            item.port           = i['server']['port']
            item.comment        = i['comment']
            rules               = i['rules']

            if rules is not None:
                for j in rules:
                    # todo support YARA rules
                    rule        = RuleSettings()
                    rule.name   = j["name"]
                    rule.packet = j["packet"]
                    rule.regex  = re.compile(rule.packet)
                    #rule.remote_address= j['remote']['address']
                    #rule.remote_port   = j['remote']['port']

                    item.rules.append(rule)

            data.protocols.append(item)

            if item.name == data.default_protocol:
                data.default_protocol_setting= item

        print(str(data))
        return data

    def __str__(self):
        return ', '.join([
            '"default_protocol": "%s"'  % self.default_protocol,
            '"protocols": [ %s ]'       % ', '.join(str(i) for i in self.protocols)])

class ProtocolSetting(object):
    def __init__(self):
        self.name       = ''
        self.address    = ''
        self.port       = 0
        self.comment    = ''
        self.rules      = []

    def __str__(self):
        return '{ %s }' % ', '.join([
            '"name": "%s"'              % self.name,
            '"server { "address": "%s", "port": %s }' % (self.address, str(self.port)),
            '"name": "%s"'              % self.comment,
            '"rules": [ %s ]'           % ', '.join(str(i) for i in self.rules)])

class RuleSettings(object):
    def __init__(self):
        self.name       = ''
        self.packet     = ''
        self.regex      = None
        #self.remote_address= ''
        #self.remote_port   = []

    def __str__(self):
        return '{ %s }' % ', '.join([
            '"name": "%s"'              % self.name,
            '"packet": "%s"'            % self.packet])

    # public
    def match(self, packet):
        m = self.regex.match(packet)

        return m
