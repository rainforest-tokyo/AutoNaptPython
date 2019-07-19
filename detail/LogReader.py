#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import glob
import json
import datetime
from threading import Lock
from Utils import Utils

from ElasticConnector import ElasticConnector

try:
    from NaptLogger import NaptLogger
except Exception as ex:
    Utils.print_exception(ex)

def read_file( filename ) :
    datetime = filename.split("_")[1].split(".")[0]
    elastic = ElasticConnector()
    f = open( filename )
    for line in f :
        data = json.loads( line )
        if data['type'] == 'recv' :
            data['cloud'] = 'sakura'
            try :
                print( data )
            except :
                pass

            elastic.store_log( data, datetime )
    f.close()

if __name__ == '__main__':
    for filename in glob.glob("/var/log/autonapt/autonapt*") :
        print(filename)
        read_file( filename )
