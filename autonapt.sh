#!/bin/bash

ulimit -n 80000
mkdir /var/log/autonapt
chmod 755 /var/log/autonapt
#python3.6 autonapt.py --bind <IP> --ports ./ports.json --protocols ./protocols.json --log /var/log/autonapt
#python3.6 autonapt.py --elastic --bind <IP> --ports ./ports.json --protocols ./protocols.json --log /var/log/autonapt
python3.6 autonapt.py --bind 172.30.0.84 --ports ./ports.json --protocols ./protocols.json --log /var/log/autonapt

