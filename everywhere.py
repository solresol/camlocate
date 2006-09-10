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
parser.add_option("-W","--west",
		  action="store",type="float",dest="longitude_start",
		  help="what longitude to start at (degrees west of Greenwich)"
		  )

parser.add_option("-E","--east",
		  action="store",type="float",dest="longitude_end",
		  help="what longitude to end at (degrees east of Greenwich)"
		  )

parser.add_option("-N","--north",
		  action="store",type="float",dest="latitude_end",
		  help="what latitude to end at (degrees north of Equator)"
		  )

parser.add_option("-S","--south",
		  action="store",type="float",dest="latitude_start",
		  help="what latitude to start at (degrees south of Equator)"
		  )

parser.add_option("-x","--longitude-increment",
		  action="store",type="float",dest="longitude_increment",
		  help="number of degrees of longitude between each step"
		  )

parser.add_option("-y","--latitude-increment",
		  action="store",type="float",dest="latitude_increment",
		  help="number of degrees of latitude between each step"
		  )

parser.add_option("-a","--average",
		  action="store",type="string",dest="average",
		  help="what kind of statistical average to use"
		  )

(options,args) = parser.parse_args()


if options.latitude_start is None: options.latitude_start = 60
if options.latitude_end is None: options.latitude_end = 60

if options.longitude_start is None: options.longitude_start = 179
if options.longitude_end is None: options.longitude_end = 179

if options.longitude_increment is None: options.longitude_increment = 0.2
if options.latitude_increment is None: options.latitude_increment = 0.2


sunrises = {}
sunsets = {}

udatfile = udat.udat(sys.stdin)
    
best_longitude = None
best_latitude = None
best_score = None

if options.average is None:
    average = udat.mean
elif options.average == 'mean':
    average = udat.mean
elif options.average == 'median':
    average = udat.median
else:
    sys.exit("Unknown averaging mechanism " + options.average)

scores = []
longitude = -options.longitude_start
while longitude < options.longitude_end:
    #print "Handling longitude",longitude
    # Normally latitude would range from -90 to + 90 (or thereabouts)
    # but I wanted to exclude the poles just while I was testing
    latitude = -options.latitude_start
    while latitude < options.latitude_end:
	score = udat.night_and_day_populations(udatfile,longitude,latitude,average)
	if score is None:
	    latitude = latitude + options.latitude_increment
	    continue
	if best_score is None:
	    best_score = score - 1
	if score > best_score:
	    #print longitude,"E ",latitude,"N is quite good:",score
	    best_score = score
	    best_latitude = latitude
	    best_longitude = longitude
	# should also show when there are several equally good scores.
	scores.append((score,latitude,longitude))
	latitude = latitude + options.latitude_increment
    
    longitude = longitude + options.longitude_increment
		
       
scores.sort()
num_to_show = int(len(scores) ** (0.5))
#num_to_show = len(scores)
if num_to_show < 1: num_to_show = 1
for (score,latitude,longitude) in scores[-num_to_show:]:
    print longitude,latitude,score


#print "Final conclusion is",best_longitude,best_latitude	



	    
