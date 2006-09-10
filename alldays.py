#!/usr/bin/env python

# $Id$

import os
os.environ["TZ"] = "GMT"
import sys
import time
import datetime
import Sun
import udat
import optparse

calculator = Sun.Sun()

feb_12_2006  = 1139764541
july_14_2017 = 1500000000
jan_28_2007 = 1170000000

print "delete from days;"
print "delete from locations;"
longitude = -180.0
while longitude < 180.0:
    latitude = -65.0
    while latitude <= 65:
	(sunrises,sunsets) = udat.sunrises_and_sunsets(latitude,longitude,feb_12_2006,jan_28_2007)
	print "insert into locations values (nextval('location_ids'),",
	print longitude,",",latitude,");"
	for (day,(sunrise,sunset)) in enumerate(zip(sunrises,sunsets)):
	    print "insert into days values (currval('location_ids'),",day,",",
	    print "cast ('"+time.asctime(time.gmtime(sunrise))+" GMT' as timestamp with time zone),",
	    print "cast ('"+time.asctime(time.gmtime(sunset))+" GMT' as timestamp with time zone));"
	latitude = latitude + 1.0
    longitude = longitude + 1.0



	    
