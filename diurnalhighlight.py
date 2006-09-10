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

parser = optparse.OptionParser()
parser.add_option("-x","--longitude",
		  action="store",type="float",dest="longitude",
		  help="what longitude (degrees east of Greenwich)"
		  )

parser.add_option("-y","--latitude",
		  action="store",type="float",dest="latitude",
		  help="what latitude (degrees north of Equator)"
		  )
parser.add_option("-s","--show",
		  action="store",type="string",dest="show",
		  help="what to show (day | night)"
		  )

(options,args) = parser.parse_args()


if options.latitude is None: sys.exit("Must specify latitude")
if options.longitude is None: sys.exit("Must specify longitude")
if options.show in ["day","night","neither","both","sunrises","sunsets"]:
    pass
else:
    sys.exit("Must specify whether you want day or night (-s argument)")

udatfile = udat.udat(sys.stdin)
    
if options.show in ["sunrises","sunsets"]:
    (sunrises,sunsets) = udat.sunrises_and_sunsets(options.latitude,options.longitude,udatfile.first_time(),udatfile.last_time())
    if options.show == "sunrises":
	data = sunrises
    else:
	data = sunsets
    for event in data:
	if event != 0.0:
	    print event,"1.0",time.strftime("%+",time.gmtime(event))
    sys.exit(0)
	

(daytimes,nighttimes) = udat.day_and_night_data(udatfile,options.latitude,options.longitude)

if options.show == "day":
    data = daytimes
elif options.show == "night":
    data = nighttimes
elif options.show == "both":
    data = daytimes + nighttimes
else:
    data = []

for day in data:
    for sample in day:
	print sample.timestamp,sample.red,sample.redstddev,sample.green,sample.greenstddev,sample.blue,sample.bluestddev




	    
