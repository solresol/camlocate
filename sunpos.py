#!/usr/bin/env python
#*********************************************************
#   This program will calculate the position of the Sun
#   using a low precision method found on page C24 of the
#   1996 Astronomical Almanac.
#
#   The method is good to 0.01 degrees in the sky over the
#   period 1950 to 2050.
#
#   QBASIC program by Keith Burnett (kburnett@geocity.com)
#   Ported to python by Greg Baker (gregb@ifost.org.au)
#
#   Work in double precision and define some constants
#

import math

#DEFDBL A-Z
pi = math.pi
#pi = 4 * ATN(1)
tpi = 2 * pi
twopi = tpi
degs = 180 / pi
rads = pi / 180
#
#   Get the days to J2000
#   h is UT in decimal hours
#   FNday only works between 1901 to 2099 - see Meeus chapter 7
#
def FNday (y, m, d, h):
 return 367 * y - 7 * (y + (m + 9) \ 12) \ 4 + 275 * m \ 9 + d - 730531.5 + h / 24

# Some compatibility assignments to match the basic names. Not sure about SQR.
def signum(i):
 # Python doesn't have a built-in signum ?!??!
 if(i < 0): return -1;
 elif(i > 0): return 1;
 else: return i;
ATN=math.atan
SQR=math.sqrt
ABS=math.fabs
SGN=signum
INT=int
#
#   define some arc cos and arc sin functions and a modified inverse
#   tangent function
#
def FNacos (x):
    s = SQR(1 - x * x)
    return ATN(s / x)

def FNasin (x):
    c = SQR(1 - x * x)
    return ATN(x / c)

#
#   the atn2 function below returns an angle in the range 0 to two pi
#   depending on the signs of x and y.
#
def FNatn2 (y, x):
    a = ATN(y / x)
    if x < 0:
     a = a + pi
    if (y < 0) and (x > 0):
     a = a + tpi
    return a


#
#   the function below returns the true integer part,
#   even for negative numbers
#
def FNipart (x):
 return SGN(x) * INT(ABS(x))
#
#   the function below returns an angle in the range
#   0 to two pi
#
def FNrange (x):
    b = x / tpi
    a = tpi * (b - FNipart(b))
    if a < 0:
      a = tpi + a
    return a

#
#   Find the ecliptic longitude of the Sun
#
def FNsun (d)
  #
  #   mean longitude of the Sun
  #
  L = FNrange(280.461 * rads + .9856474# * rads * d)
  #
  #   mean anomaly of the Sun
  #
  g = FNrange(357.528 * rads + .9856003# * rads * d)
  #
  #   Ecliptic longitude of the Sun
  #
  return FNrange(L + 1.915 * rads * SIN(g) + .02 * rads * SIN(2 * g))
  #
  #   Ecliptic latitude is assumed to be zero by definition
  #
#
#
#
INPUT = raw_input
#
#    get the date and time from the user
#
y= string.atoi(INPUT( "  year  : "))
m= string.atoi(INPUT( "  month : "))
day= string.atoi(INPUT( "  day   : "))
h= string.atoi(INPUT( "hour UT : "))
mins= string.atoi(INPUT( " minute : "))

h = h + mins / 60
d = FNday(y, m, day, h)
#
#   Use FNsun to find the ecliptic longitude of the
#   Sun
#
lambda = FNsun(d)
#
#   Obliquity of the ecliptic
#
obliq = 23.439 * rads - .0000004# * rads * d
#
#   Find the RA and DEC of the Sun
#
alpha = FNatn2(COS(obliq) * SIN(lambda), COS(lambda))
delta = FNasin(SIN(obliq) * SIN(lambda))
#
#   Find the Earth - Sun distance
#
r = 1.00014 - .01671 * COS(g) - .00014 * COS(2 * g)
#
#   Find the Equation of Time
#
equation = (L - alpha) * degs * 4
#
#   print results in decimal form
#
print
print "Position of Sun"
print "==============="
print
print "     days : %5.5f" % d
print "longitude : %5.2f" % (lambda * degs)
print "       RA : %5.3f" % (alpha * degs / 15.0)
print "      DEC : %5.2f" % (delta * degs)
print " distance : %5.5f" % (r)
print "eq time   : %5.2f" % (equation)
#*********************************************************
