#! /bin/bash

wget https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
wget https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz
wget https://geolite.maxmind.com/download/geoip/database/GeoLite2-ASN.tar.gz

tar xvfz GeoLite2-City.tar.gz
tar xvfz GeoLite2-Country.tar.gz
tar xvfz GeoLite2-ASN.tar.gz

cp */*.mmdb .
