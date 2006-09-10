# $Id$

import time
import string
import Sun

calculator = Sun.Sun()


class imagesummary:
    def __init__(self,timestamp,lineremainder):
	[red,redstddev,green,greenstddev,blue,bluestddev] = lineremainder
	self.timestamp = timestamp
	self.red = string.atof(red)
	self.redstddev = string.atof(redstddev)
	self.blue = string.atof(blue)
	self.bluestddev = string.atof(bluestddev)
	self.green = string.atof(green)
	self.greenstddev = string.atof(greenstddev)



class mean:
    def __init__(self,imagesummaries):
	(red,blue,green) = (0.0,0.0,0.0)
	for img in imagesummaries:
	    (red,blue,green) = (red + img.red,blue + img.blue,green + img.green)
	(self.red,self.blue,self.green) = (red / len(imagesummaries), blue / len(imagesummaries), green / len(imagesummaries))
	(reddev,bluedev,greendev) = (0.0,0.0,0.)
	for img in imagesummaries:
	    reddev = reddev + (self.red - img.red) ** 2
	    bluedev = bluedev +  (self.blue - img.blue) ** 2
	    greendev = greendev + (self.green - img.green) ** 2
	if len(imagesummaries) > 1:
	    self.redstddev = (reddev / (len(imagesummaries)-1)) ** (0.5)
	    self.greenstddev = (greendev / (len(imagesummaries)-1)) ** (0.5)
	    self.bluestddev = (bluedev / (len(imagesummaries)-1)) ** (0.5)
	else:
	    self.redstddev = 0.0
	    self.greenstddev = 0.0
	    self.bluestddev = 0.0
	

class median:
    def __init__(self,imagesummaries):
	sorted = [((x.red ** 2 + x.green ** 2 + x.blue ** 2) ** 0.5,x,i) for (i,x) in enumerate(imagesummaries)]
	sorted.sort()
	where = int(len(sorted)/2)
	(magnitude,x,i) = sorted[where]
	self.red = x.red
	self.green = x.green
	self.blue = x.blue
	self.redstddev = x.redstddev
	self.greenstddev = x.greenstddev
	self.bluestddev = x.bluestddev
	


class udat:
    def __init__(self,fd):
	self.data = {}
	for line in fd:
	    if line == '': continue
	    if line[0] == '#': continue
	    fields = line.split()
	    if len(fields) != 7: continue
	    time_of_line = time.mktime(time.strptime(fields[0],"%Y-%b-%d@%H:%M:%S"))
	    #try:
	    self.data[time_of_line] = imagesummary(time_of_line,fields[1:])
	    #except:
	    #pass
	self.times = self.data.keys()
	self.times.sort()
	self.cache = (None,0)
    def first_time(self): return self.times[0]
    def last_time(self): return self.times[-1]
    def between(self,starttime,stoptime):
	# I could implement some wondefully smart method for a log log N
	# look up time in the self.times array. 
	# Or, I could observe that the majority of the time we're repeatedly
	# calling this function with something soon after the previous 
	# starttime.
	(previous_starttime,previous_index) = self.cache
	if previous_starttime is not None and previous_starttime <= starttime:
	    start_idx = previous_index
	    #print "Cache trick worked."
	else:
	    #print "Cache trick failed because",starttime,previous_starttime
	    start_idx = 0
	for i in range(start_idx,len(self.times)):
	    t = self.times[i]
	    if t >= starttime:
		start_idx = i
		break
	else:
	    return []
	ret = []
	self.cache = (starttime,start_idx)
	for i in range(start_idx,len(self.times)):
	    t = self.times[i]
	    if t <= stoptime:
		ret.append(self.data[t])
	    else:
		return ret
	else:
	    return ret
	pass
	    
	    
def sunrises_and_sunsets(latitude,longitude,starttime,stoptime):
    sunrises = []
    sunsets = []
    dayloop = starttime
    lastday = stoptime

    while dayloop <= lastday:
	daytuple = time.gmtime(dayloop)
	(sunrise,sunset) = calculator.sunRiseSet(daytuple[0],daytuple[1],daytuple[2],longitude,latitude)
	    
	daystart = time.mktime((daytuple[0],daytuple[1],daytuple[2],0,0,0,daytuple[6],daytuple[7],daytuple[8]))
	sunrises.append(daystart + sunrise * 3600)
	sunsets.append(daystart + sunset * 3600)
	dayloop = dayloop + 86400

    # make sure there is a sunrise before and after every sunset
    if sunrises[0] > sunsets[0]:
	sunrises = [0.0] + sunrises
	sunsets = sunsets + [stoptime + 1]
    sunrises.append(stoptime+2)
    return (sunrises,sunsets)
 

def day_and_night_data(udatfile,latitude,longitude):
    first_data = udatfile.first_time()
    last_data = udatfile.last_time()
    score = 0.0
    (sunrises,sunsets) = sunrises_and_sunsets(latitude,longitude,first_data,last_data)
    #print "SUNRISES"
    #print sunrises
    #print "SUNSETS"
    #print sunsets
    daytimes = []
    nighttimes = []
    for i in range(len(sunsets)):
	daytimes.append(udatfile.between(sunrises[i],sunsets[i]))
	nighttimes.append(udatfile.between(sunsets[i],sunrises[i+1]))
    return (daytimes,nighttimes)



def night_and_day_populations(udatfile,latitude,longitude,average=mean):
    (daytimes,nighttimes) = day_and_night_data(udatfile,latitude,longitude)
    # We can't do anything with a daytime or nighttime which is of zero
    # length. All we can do is ignore it.
    day_stat = mean(map(average, (filter(lambda x: len(x) > 1, daytimes))))
    night_stat = mean(map(average,(filter(lambda x: len(x) > 1, nighttimes))))
    # it would be nice to know if stddevs of day and night differ.
    # I think they shouldn't.
    # Should also print out stats for each colour
    red_part = (day_stat.red - night_stat.red) / day_stat.redstddev
    blue_part = (day_stat.blue - night_stat.blue) / day_stat.bluestddev
    green_part = (day_stat.green - night_stat.green) / day_stat.greenstddev
    score = red_part + blue_part + green_part
    #print latitude,longitude,score,red_part,green_part,blue_part
    #print "RED: ",day_stat.red, night_stat.red, day_stat.redstddev, night_stat.redstddev
    #print "GREEN: ",day_stat.green, night_stat.green, day_stat.greenstddev, night_stat.greenstddev
    #print "BLUE: ",day_stat.blue, night_stat.blue, day_stat.bluestddev, night_stat.bluestddev
    return score

