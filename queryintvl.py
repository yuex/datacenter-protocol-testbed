#!/usr/bin/env python
import math
import sys
import random
import pointcurve

if len(sys.argv) <= 3:
    sys.stderr.write("%s: USAGE %s duration ip_file src_ip\n" % (sys.argv[0], sys.argv[0]))
    sys.exit()

l = 7.1
queryarr = lambda x: 1 - math.exp(-l*x)
#queryintvl_r = lambda y: math.log(1-y)/(-l)

queryintvl_r = pointcurve.pointcurve('queryintvl.cdf').ytox

need = float(sys.argv[1])
have = 0

f = open(sys.argv[2])
ip = f.readlines()
ip = [ t.replace('\n','') for t in ip ]
f.close()

while True:
    intvl = random.random()
    intvl = queryintvl_r(intvl)
    have += intvl
    if have > need:
        sys.stderr.write("\nlast intvl is %f, if included we have %f sec\n" % (intvl, have))
        break
    
    size = 2048
    
    src = sys.argv[3]
    #for dst in ip:
        #if dst == src: continue
        #sys.stdout.write("%.9f %s %d\n" % (intvl, dst, size))
        #intvl = 0
    sys.stdout.write("%.9f %s %d\n" % (intvl, src, size))
