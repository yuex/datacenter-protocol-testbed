#!/usr/bin/env python
import math
import sys
import random

if len(sys.argv) <= 3:
    sys.stderr.write("%s: USAGE %s duration ip_file src_ip\n" % (sys.argv[0], sys.argv[0]))
    sys.exit()

# l = 3.5
# k = 4
# def backsize(x):
#     x = math.log10(x)
#     return 1 - math.exp(-(x/l)**k)
# 
# def backsize_r(y):
#     x = l * (-math.log(1-y)) **(1/k)
#     return 10**x

import pointcurve
backsize_r = pointcurve.pointcurve('datasize.cdf').ytox
backintvl_r = pointcurve.pointcurve('dataintvl.cdf.light').ytox

# import backintvldistb
# backintvl_r = backintvldistb.ytox
#sl = 0.4
#sk = 0.32
#def backintvl(x):
    #return 1 - math.exp(-(x/sl)**sk)
    
#def backintvl_r(y):
    #return sl * (-math.log(1-y)) **(1/sk)

need = float(sys.argv[1])
have = 0

f = open(sys.argv[2])
ip = f.readlines()
ip = [ t.replace('\n','') for t in ip ]
f.close()

while True:
    while True:
        intvl = random.random()
        intvl = backintvl_r(intvl)
        if intvl != False:
            break

    #if intvl < 0.0001:
        #continue
    
    #scaled intvl to tenth
    #intvl = intvl / 10
    
    have += intvl
    if have > need:
        sys.stderr.write("\nlast intvl is %f, if included we have %f sec\n" % (intvl, have))
        break


    while True:
        size = random.random()
        size = backsize_r(size)
        if size != False:
            break

    if size - math.floor(size) >= math.ceil(size) - size:
        size = int(math.ceil(size))
    else:
        size = int(math.floor(size))
    
    #src = sys.argv[3]
    #dst = src
    #while dst == src:
        #dst = random.choice(ip)
    dst = sys.argv[3]



    #sys.stdout.write("%.9f %s %s %d\n" % (intvl, src, dst, size))
    sys.stdout.write("%.9f %s %d\n" % (intvl, dst, size))
