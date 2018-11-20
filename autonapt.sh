#!/bin/bash

ulimit -n 65536
python3.6 autonapt.py --elastic --bind 172.30.0.142 --ports ./ports.json --protocols ./protocols.json --log /var/log/autonapt

