#!/usr/bin/env python

import string
import time
import sys
import os
import math
import InvSun
os.environ['TZ'] = 'GMT'

def balance(numlist):
    l = [ (x[1],x[0]) for x in enumerate(numlist) ]
    l.sort()
    c = len(numlist)
    best_balance = sum([x[0] for x in l])
    best_balance_index = None
    best_balance_orig_index = None
    for i in range(1,len(l)):
	night = sum([x[0] for x in l[:i]]) / (1.0*i)
	day = sum([x[0] for x in l[i:]]) / (1.0*(c-i))
	b = night + day - (2 * l[i][0])
	if abs(b) < best_balance:
	    best_balance = abs(b)
	    best_balance_index = i
	    best_balance_orig_index = l[i][1]
    return (l[best_balance_index][0],best_balance_orig_index)


def sunrise_sunset(date,threshold,values,times):
    currently_below_threshold = None
    previous_time = None
    previous_threshold_crossing = None
    current_status_times = []
    current_values = []
    oscillations = []
    current_values = []
    for (v,t) in zip(values,times):
	if currently_below_threshold is None:
	    currently_below_threshold = v < threshold
	    previous_time = t
	    previous_threshold_crossing = t
	this_below_threshold = v < threshold
	if len(current_values) == 0:
	    previous_below_threshold = this_below_threshold
	else:
	    previous_below_threshold = current_values[-1] < threshold
	if this_below_threshold != previous_below_threshold:
	    # real threshold crossing, perhaps?
	    # let's see if seems suspiciously short
	    if (len(current_status_times) < 7) and len(oscillations) > 0:
		#print "I don't believe this was extreme enough:",len(current_status_times),"sample(s):",current_values,"against a threshold of",threshold,"between",current_status_times[0],"and",current_status_times[-1]
		# hmm, no, I don't believe it. Of course, this stuffs up
		# near the arctic and antarctic, when I should believe a day
		# length below 30 minutes; and what if it's the last 30 minutes
		# of the day or something?
		last_osc = oscillations[-1]
		# start unwinding the last oscillation
		oscillations = oscillations[:-1]
		previous_threshold_crossing = last_osc[1][0]
		current_status_times = last_osc[1] + current_status_times + [t]
		current_values = last_osc[2] + current_values + [v]
	    else:
		# ok, I believe it
		oscillations.append((currently_below_threshold,current_status_times[:],current_values[:]))
		previous_threshold_crossing = t
		current_status_times = [t]
		current_values = [v]
		currently_below_threshold = this_below_threshold
	else:
	    # there was no threshold crossing... boring!
	    current_status_times.append(t)
	    current_values.append(v)
	previous_time = t
    currently_below_threshold = sum(current_values) / len(current_values) < threshold
    oscillations.append((currently_below_threshold,current_status_times[:],current_values[:]))
    #     i = 0
    #     while i < len(oscillations):
    # 	# unfortunately, the following stuffs up near the artic / antarctic
    # 	# circle when you might get less than 15 minutes of daylight or night
    # 	if len(oscillations) > (i + 2) and len(oscillations[i+1][1]) < 3:
    # 	    refined_oscillations.append((oscillations[i][0],oscillations[i][1] + oscillations[i+1][1] + oscillations[i+2][1]))
    # 	    print "Squashing down the time in",oscillations[i+1][1]
    # 	    i = i + 3
    # 	else:
    # 	    refined_oscillations.append(oscillations[i])
    # 	    i = i + 1
    first_time = times[0]
    last_time = times[-1]
    for (delin,when,whatvalues) in oscillations:
	#l2_average = sum([((x-threshold)*abs(x-threshold)) for x in whatvalues]) / len(whatvalues)
	l2_average = sum(whatvalues) / len(whatvalues)
	#if l2_average < threshold:
	#    print "Night",
	#else:
	#    print "Day",
	#if when[0] != first_time: print "from",when[0],
	#if when[-1] != last_time: print "until",when[-1],
	#print "(",len(when),"samples with l2_average ",l2_average,")"
    if len(oscillations) == 3:
	first = oscillations[0]
	second = oscillations[1]
	third = oscillations[2]
	first_boundary = time.mktime(time.strptime(date + " " + first[1][-1],"%Y-%b-%d %H:%M:%S"))
	second_boundary = time.mktime(time.strptime(date + " " + second[1][0],"%Y-%b-%d %H:%M:%S"))
	third_boundary = time.mktime(time.strptime(date + " " + second[1][-1],"%Y-%b-%d %H:%M:%S"))
	fourth_boundary = time.mktime(time.strptime(date + " " + third[1][0],"%Y-%b-%d %H:%M:%S"))
	
	start_with_day = sum(first[2]) / len(first) > threshold
	#if start_with_day: 
	#    print "Sunset",
	#else:
	#    print "Sunrise",
	#print "between",first[1][-1],"and",second[1][0]
	#if start_with_day:
	#    print "Sunrise",
	#else:
	#    print "Sunset",
	#print "between",second[1][-1],"and",third[1][0]
	if start_with_day:
	    sunset = (first_boundary + second_boundary) / 2
	    sunrise = (third_boundary + fourth_boundary) / 2
	    midnight = (sunset + sunrise) / 2
	    noon = midnight + 43200
	else:
	    sunrise = (first_boundary + second_boundary) / 2
	    sunset = (third_boundary + fourth_boundary) / 2
	    noon = (sunrise + sunset) / 2
	    midnight = noon - 43200
	#sunrise_h = (string.atof(time.strftime("%H",time.gmtime(sunrise)))
	#	     + (string.atof(time.strftime("%M",time.gmtime(sunrise)))/60)
	#	     + (string.atof(time.strftime("%S",time.gmtime(sunrise)))/3600)
	#	     )
	#sunset_h = (string.atof(time.strftime("%H",time.gmtime(sunset)))
	#            + (string.atof(time.strftime("%M",time.gmtime(sunset)))/60)
	#		    + (string.atof(time.strftime("%S",time.gmtime(sunset)))/3600)
	#	    )
	#print "Sunrise/sunset around",time.strftime("%H:%M:%S",time.gmtime(sunrise)),"and",time.strftime("%H:%M:%S",time.gmtime(sunset))
	return ((sunrise,"SUNRISE"),(sunset,"SUNSET"))
	#print "Guesses..."
	#print "Noon around",time.strftime("%H:%M:%S",time.gmtime(noon))
	#print "Midnight around",time.strftime("%H:%M:%S",time.gmtime(midnight))
	how_far_around = 360 * ((midnight % 86400) / 86400)
	if how_far_around > 180: how_far_around = how_far_around - 360
	#if how_far_around > 0:
	#    print "I think this site must be ",how_far_around,"degrees WEST"
	#else:
	#    print "I think this site must be ",(-how_far_around),"degrees EAST"
	print tag,
	print how_far_around,
	daylength = sunset - sunrise
	if daylength < 0: daylength = daylength + 86400
	#print "Daylength is",daylength,"seconds around",noon
	what_daynumber = time.strftime("%j",time.gmtime(noon))
	# 22 December is one extreme (9 days off the year end); we actually 
	# need to know how many years
	# since the last leap year too, but I haven't included that.
	sinus = (math.cos(math.pi * 2 * (string.atof(what_daynumber)+9)/365.25))
	# horrible blow-up around the equinoxes. Can't do much about it really
	longest_daylight = 43200 + ((daylength - 43200) / sinus)
	#print "Daylight at this location would be ",longest_daylight,"seconds long on Dec 22"
	midnight_to_dawn_radians = (math.pi * (1 - (longest_daylight / 86400)))
	#print "So the sun went through",midnight_to_dawn_radians,"radians between midnight and dawn."
	#print "(Which is",(midnight_to_dawn_radians * (180 / math.pi))," degrees)"
	latitude = 2 * (90 - 22.5) * ((midnight_to_dawn_radians / math.pi) - 0.5)
	print latitude,longest_daylight
	#if latitude > 0:
	#    print "The latitude is around",latitude," NORTH"
	#else:
	#    print "The latitude is around",(-latitude)," SOUTH"
	
	
	
	    
    else:
	return (None,None)
	print "#",tag," Not sure about sunrise / sunset times."
	

	    
	

today = None
history = []
todaysdata = []
reds = []
greens = []
blues = []
times = []
red_results = []
green_results = []
blue_results = []

for line in sys.stdin:
    if line == '': continue
    if line[0] == '#': continue
    fields = line.split()
    [whenday,whentime] = fields[0].split('@')
    [year,month,day] = whenday.split('-')
    #if len(day) == 1:
    #	whenday = year + "-" + month + "-0" + day
    time_of_line = time.strptime(whenday+" "+whentime,"%Y-%b-%d %H:%M:%S")
    if today is None:
	today = whenday
    if whenday == today:
	try:
	    reds.append(string.atof(fields[1]))
	    greens.append(string.atof(fields[3]))
	    blues.append(string.atof(fields[5]))
	    times.append(whentime)
        except:
	    pass
    else:
	(r,r_idx) = balance(reds)
	(g,g_idx) = balance(greens)
	(b,b_idx) = balance(blues)
	t = `time.mktime(time.strptime(today,"%Y-%b-%d"))`
	(r_sunrise,r_sunset) = sunrise_sunset(today,r,reds,times)
	(g_sunrise,g_sunset) = sunrise_sunset(today,g,reds,times)
	(b_sunrise,b_sunset) = sunrise_sunset(today,b,reds,times)
	if r_sunrise is not None:
	    red_results.append(r_sunrise)
	    red_results.append(r_sunset)
	if g_sunrise is not None:
	    green_results.append(g_sunrise)
	    green_results.append(g_sunset)
	if b_sunrise is not None:
	    blue_results.append(b_sunrise)
	    blue_results.append(b_sunset)

	today = whenday
	reds = []
	greens = []
	blues = []
	times = []


locations = []

for (name,data) in [("RED",red_results),("GREEN",green_results),("BLUE",blue_results)]:
    data.sort()
    if data[0][1] == "SUNSET":
	data = data[1:]
    for i in range(0,len(data),2):
	try:
	    sunrise = data[i][0]
	    sunset = data[i+1][0]
	    (longitude,latitude) = InvSun.get_location(sunrise,sunset)
	    if longitude < -180: longitude = longitude + 360
	    print name,"says",longitude,latitude,"because",sunrise,sunset
	    locations.append((longitude,latitude))
	except OverflowError:
	    pass
	except IndexError:
	    pass


longitudes = [x[0] for x in locations]
latitudes = [x[1] for x in locations]

longitudes.sort()
latitudes.sort()

halfway = int(len(locations) / 2)

print "AVERAGE says",longitudes[halfway],latitudes[halfway],"because _ _"
	
	
