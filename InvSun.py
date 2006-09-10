import math
import time
from Sun import Sun

#Constants
DEGRAD=math.pi/180.0 #Degree/radian conversion ratios
RADEG=180.0/math.pi

# Outputs location, given sunrise and set times and date.
# Assumes sunrise/set occurs when the sun's centre is 35" below the horizon.

# Accurate to about a minute of arc, or about 2 kilometres at any reasonable
# latitude.
# (note that a minute's difference in sunrise or sunset is about 30 km)

# Becomes more inaccurate further from the equator, and, as
# one would expect, is not that useful in times when the sun is
# either above or below the horizon for the whole day.

def getloclist(*times):
    #Takes either individual arguments, each a (sunrise,sunset) tuple, or
    # alternatively, a list of such tuples. The times are all in
    # time.time(unix) time.

    if type(times[0])==type([]): times=times[0]

    #Change to 9-tuple
    ttimes=[] 
    for i in times: ttimes.append([time.gmtime(i[0]),time.gmtime(i[1])])

    #Get equinoxes
    years={}
    for i in ttimes:
        if not (i[0][0] in years): years[i[0][0]]=1
        if not (i[1][0] in years): years[i[1][0]]=1

    for i in years: years[i]=getequinoxes(i)

    avlat=[]
    avlon=[]

    #Calculate, average, and drop equinoxes.
    for i in range(len(times)):
        flag=1
        equinoxes=years[ttimes[i][0][0]]
        midday=(times[i][0]+times[i][1])/2

        #Test for equinoxes; (exclusion zone calculated and tested, then
        #expanded slightly to allow for small errors, etcetera)
        if midday-equinoxes[0]>0 and midday-equinoxes[0]<3600*12:flag=0
        if equinoxes[0]-midday>0 and equinoxes[0]-midday<3600*35:flag=0

        #September equinox
        if midday-equinoxes[1]>0 and midday-equinoxes[1]<3600*35:flag=0
        if equinoxes[1]-midday>0 and equinoxes[1]-midday<3600*12:flag=0

        if flag:
            lon,lat=get_location(times[i][0],times[i][1])
            avlat.append(lat)
            avlon.append(lon)
    #Chuck out anything more than 1 standard deviation out
    #(this means that a few days out by a large margin shouldn't
    #affect the result as much as they otherwise would).
    
    lasd,lamean=sdm(avlat)
    losd,lomean=sdm(avlon)
    avlat=filter(lambda x:abs(x-lamean)<=lasd,avlat)
    avlon=filter(lambda x:abs(x-lomean)<=losd,avlon)

    #Normalise and return lon/lat pair. (lon in range -180 to 180)
    longitude=norm(mean(avlon))
    latitude=norm(mean(avlat))
    
    return (longitude,latitude)

def get_location(sunrise,sunset,altitude=0):
    if (type(sunrise),type(sunset)) == (type(0.0),type(0.0)):
	sunrise = time.gmtime(sunrise)
	sunset = time.gmtime(sunset)
    #if (type(sunrise),type(sunset)) != (type((0,)),type((0,))):
    #raise TypeError,"Sunset and sunrise should be given as either seconds since 1970, or a 9-tuple as you would get from time.gmtime()"
    if time.mktime(sunset) < time.mktime(sunrise): raise ValueError,(sunrise,sunset)
    if time.mktime(sunrise) + 86400 < time.mktime(sunset): 
	raise OverflowError,(sunrise,sunset)
    year = sunrise[0]
    month = sunrise[1]
    day = sunrise[2]
    sunrise_h = sunrise[3] + (sunrise[4] / 60.0) + (sunrise[5] / 3600.0)
    sunset_h = sunset[3] + (sunset[4] / 60.0) + (sunset[5] / 3600.0)
    if sunset_h < sunrise_h: sunset_h = sunset_h + 24
    #print year,month,day,sunrise_h,sunset_h
    return getloc(year,month,day,sunrise_h,sunset_h,altitude)

#Usage: getloc (year,month,day,sunrise,sunset) where sunrise, sunset are in GMT.
def getloc(year,month,day,sunrise,sunset,altitude=0):
    if sunrise>sunset: #Handle sunrise from day before not being negative, as
                       #it really should be.
        sunrise=sunrise-24.0
    
    tester=Sun()
    daylen=sunset-sunrise
    darc=cosd(7.5*daylen) #diurnal arc

    #Latitude, round I
    days=tester.daysSince2000Jan0(year,month,day) + 0.5 
    rasc,dec,radius=tester.sunRADec(days) #right ascension,declination,radius of sun.
    alt=-35.0/60.0-0.2666/radius

    #Account for altitude.
    alt-=acosd(6378.0/(6378.0+altitude))

    #Precalculated sines
    b=sind(alt)
    c=sind(dec)

    #Cribs
    crib1=darc*darc*c*c-darc*darc
    crib2=c*c-crib1
    crib3=2*b*c

    #Calculation
    uroot=crib3**2-4*(b*b+crib1)*crib2
    if uroot<0: uroot=-uroot
    uroot=math.sqrt(uroot)/(2*crib2)
    rest=crib3/(2*crib2)

    #Choose best of the 2 possible solutions
    try:
        lat_i=asind(rest-uroot)
        i=abs(diff(tester.sunRiseSet(year,month,day,0,lat_i))-daylen)
    except ValueError:
        i=1000
    try:
        lat_ii=asind(rest+uroot)
        ii=abs(diff(tester.sunRiseSet(year,month,day,0,lat_ii))-daylen)
    except ValueError:
        ii=1000
    if i<ii: lat=lat_i
    else: lat=lat_ii

    #Find longitude
    midday=(sunset+sunrise)/2
    gmmid=av(tester.sunRiseSet(year,month,day,0,lat))
    lon=-(midday-gmmid)*15

    #Latitude, round II (using longitude)
    d=tester.daysSince2000Jan0(year,month,day) + 0.5 - lon/360.0
    RA__,dec,radius=tester.sunRADec(d)
    alt=-35.0/60.0-0.2666/radius

    #Account for altitude.
    alt-=acosd(6378.0/(6378.0+altitude))

    #Precalculated sines
    b=sind(alt)
    c=sind(dec)

    #Cribs
    crib1=darc*darc*c*c-darc*darc
    crib2=c*c-crib1
    crib3=2*b*c

    #Calculation
    uroot=crib3**2-4*(b*b+crib1)*crib2
    if uroot<0: uroot=-uroot
    uroot=math.sqrt(uroot)/(2*crib2)
    rest=crib3/(2*crib2)

    #Choose best of the 2 possible solutions
    try:
        lat_i=asind(rest-uroot)
        i=abs(diff(tester.sunRiseSet(year,month,day,0,lat_i))-daylen)
    except ValueError:
        i=1000
    try:
        lat_ii=asind(rest+uroot)
        ii=abs(diff(tester.sunRiseSet(year,month,day,0,lat_ii))-daylen)
    except ValueError:
        ii=1000
    if i<ii: lat=lat_i
    else: lat=lat_ii

    #Return tuple in similar fashion to Sun.sunRiseSet
    return (lon,lat)

def getequinoxes(year): #Get the equinoxes for a particular year in unix time.
    m=(year-2000.0)/1000.0

    #Vernal equinox
    ve=2451623.80984+365242.37404*m+0.05169*m*m-0.00411*m*m*m-0.00057*m*m*m*m

    #Autumnal equinox
    ae=2451810.21715+365242.01767*m-0.11575*m*m+0.00337*m*m*m+0.00078*m*m*m*m

    # Fairly accurate (~1 minute)
    return (ve-2440587.5)*3600*24,(ae-2440587.5)*3600*24 #Convert to unix time.
    
def diff((a,b)): return b-a #Difference

def av((a,b)): return (a+b)/2 #Average

def sdm(lst): #Standard deviation and mean
    m=mean(lst)
    total=0.0 #Needs to be floating-point.
    for i in lst:total+=(i-m)**2
    total/=len(lst)
    total=math.sqrt(total)
    return total,m

def norm(x):  #Normalise an angle to between -180 and 180 degrees.
	x=x%360
	if x>180:x-=360
	return x

def mean(lst): #Mean
    return sum(lst)/len(lst)

#Trig functions in degrees
def sind(x): return math.sin(x * DEGRAD)
def cosd(x): return math.cos(x * DEGRAD)
def tand(x): return math.tan(x * DEGRAD)
def cotd(x): return math.cot(x * DEGRAD)
def asind(x): return math.asin(x) * RADEG
def acosd(x): return math.acos(x) * RADEG
def atand(x): return math.atan(x) * RADEG
def atan2d(x,y): return math.atan2(x, y) * RADEG
