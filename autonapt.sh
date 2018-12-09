#!/bin/bash

ulimit -n 80000
python3.6 autonapt.py --elastic --bind 133.34.157.64 --ports ./ports.json --protocols ./protocols.json --log /var/log/autonapt

