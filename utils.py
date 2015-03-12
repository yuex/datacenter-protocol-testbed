#!/usr/bin/env python
import datetime
import time
import sys

today = datetime.datetime.today()
today = [today.year, today.month, today.day]
today = ' '.join([str(t) for t in today])
today = time.mktime(time.strptime(today, "%Y %m %d"))

BACKLOG = 2048
BUFFSIZE = 4096
QUERYSIZE = 2048
if sys.version[0] == '2':
    def magic(foo):
        return str(foo)
elif sys.version[0] == '3':
    def magic(foo):
        return bytes(str(foo).encode('utf-8'))
else:
    sys.stderr.write("python version not recoganized\n")
    sys.exit()

#def nicesize(size):
    #gib = 1024**3
    #mib = 1024**2
    #kib = 1024

    #size = float(size)

    #if size > gib:
        #return '%.3f GiB' % (size/gib)
    #elif size > mib:
        #return '%.3f MiB' % (size/mib)
    #elif size > kib:
        #return '%.3f KiB' % (size/kib)
    #else:
        #return '%.3f Byt' % size

def nicesize(size):
    return int( size )

def nicetime(time):
    return time

