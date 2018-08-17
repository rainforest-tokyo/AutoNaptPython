#!/bin/bash

ulimit -n 65536
python3.6 autonapt.py --elastic --ports ./ports.json --protocols ./protocols.json --log /var/log/autoapt.log

