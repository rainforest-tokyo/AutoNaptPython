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
from types import MethodType

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/detail')

from Utils import Utils

try:
    from AutoNapt import AutoNapt
except Exception as ex:
    Utils.print_exception(ex)

def expects_type(self, name, cls):
    Utils.expects_type(cls, self, name)

def main(argv):
    try:
        # TypeError: can't set attributes of built-in/extension type 'object'
        #object.expects = MethodType(expects_type, object)

        return AutoNapt.main(argv)
    except Exception as ex:
        Utils.print_exception(ex)
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
