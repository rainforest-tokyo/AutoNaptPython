#!/bin/bash

ulimit -n 80000
mkdir /var/log/autonapt
chmod 755 /var/log/autonapt
#python3.6 autonapt.py --elastic --bind 133.34.157.64 --ports ./ports.json --protocols ./protocols.json --log /var/log/autonapt
python3.6 autonapt.py --elastic --bind 0.0.0.0 --ports ./ports.json --protocols ./protocols.json --log /var/log/autonapt

