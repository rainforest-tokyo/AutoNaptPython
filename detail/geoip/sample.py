import geoip2.database

reader = geoip2.database.Reader('./GeoLite2-City.mmdb')

response = reader.city('128.101.101.101')

print (response.country.iso_code)
print (response.country.name)

print (response.subdivisions.most_specific.name)
#print (response.subdivisions.most_specific.iso_code)

print (response.postal.code)

print (response.location.latitude)
print (response.location.longitude)

reader = geoip2.database.Reader('./GeoLite2-ASN.mmdb')
response = reader.asn('1.128.0.0')

print (response.autonomous_system_organization)

