#!/usr/bin/env python

# $Header$

import sys
import string
import time
import math

previous_r = None
previous_g = None
previous_b = None
rolling_r = []
rolling_g = []
rolling_b = []
sum_r = 0.0
count_r = 0.0
sum_g = 0.0
count_g = 0.0
sum_b = 0.0
count_b = 0.0

output = []
roll_length = 144
sample_interval = 300
# should actually have the rolling average be 12 hours rather than
# just the last 144 samples (which might include holes)


for line in sys.stdin:
    if line[0] == '#':
	print line
	continue
    columns = string.split(line)
    when = time.strftime('%Y-%b-%d@%H:%M:%S',time.gmtime(time.mktime(time.strptime(columns[0],'%Y-%b-%d@%H:%M:%S')) + ((roll_length * sample_interval / 2.0))))
    r = string.atof(columns[1])
    g = string.atof(columns[3])
    b = string.atof(columns[5])
    sum_r = sum_r + r
    sum_g = sum_g + g
    sum_b = sum_b + b
    count_r = count_r + 1
    count_g = count_g + 1
    count_b = count_b + 1
    r_stddev = string.atof(columns[2])
    g_stddev = string.atof(columns[4])
    b_stddev = string.atof(columns[6])
    log_r = math.log(r)
    log_g = math.log(g)
    log_b = math.log(b)
    rolling_r.append(r)
    rolling_g.append(g)
    rolling_b.append(b)


    r_r = sum(rolling_r) / len(rolling_r)
    r_g = sum(rolling_g) / len(rolling_g)
    r_b = sum(rolling_b) / len(rolling_b)

    if len(rolling_r) >= roll_length:
	rolling_r = rolling_r[1:]
	rolling_g = rolling_g[1:]
	rolling_b = rolling_b[1:]
        
    print when,r_r,r_g,r_b
    previous_r = r
    previous_g = g
    previous_b = b 
    previous_log_r = log_r
    previous_log_g = log_g
    previous_log_b = log_b

mean_r = sum_r / count_r
mean_g = sum_g / count_g
mean_b = sum_b / count_b


		      
