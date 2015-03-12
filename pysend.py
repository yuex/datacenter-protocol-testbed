#!/usr/bin/env python
import time
import sys
from timeclient import *


if len(sys.argv) < 3:
    sys.stderr.write("%s: USAGE %s [back|query] intvlfile ip_file\n" % (sys.argv[0], sys.argv[0]))
    sys.exit()

MODE = sys.argv[1]
FILE = sys.argv[2]
BACKPORT = 1400
QUERYPORT = 1500

f = open(FILE)
data = f.readlines()
f.close()
data = [ t.replace('\n','') for t in data ]

if len(sys.argv) >3:
    ipfile = open(sys.argv[3])
    iplist = ipfile.readlines()
    ipfile.close()
    iplist = [ t.replace('\n','') for t in iplist ]


if MODE == 'back' or MODE == 'size':

    MODE = 'size'

    class backit(threading.Thread):
        def __init__(self, addr, size):
            threading.Thread.__init__(self)
            self._addr = addr
            self._size = size
        def run(self):
            t = timethread(self._addr, MODE, self._size)
            start = time.time()
            t.start()
            t.join()
            end = time.time()
            duration = end - start
            sys.stdout.write('%s %s summary %s %.9f %.9f %.9f\n' % (self._addr[0], self._addr[1], self._size, duration, start, end))
            sys.stdout.flush()

    for t in data:
        intvl,host,size = t.split()
        intvl = float(intvl)
        size = int(size)
        addr = (host, BACKPORT)

        time.sleep(intvl)
        #backit(addr,size).start()
        timethread(addr, MODE, size, detail=True).start()

elif MODE == 'query':

    class queryall(threading.Thread):
        def __init__(self, myip, parm):
            threading.Thread.__init__(self)
            self._myip = myip
            self._parm = parm

        def run(self):
            queue = []
            for host in iplist:
                if self._myip == host:
                    continue
                addr = (host, QUERYPORT)
                t = timethread(addr, MODE, self._parm, detail=True)
                queue.append(t)
            start = time.time()
            for sendthread in queue:
                sendthread.start()

            latest = 0
            for sendthread in queue:
                sendthread.join()
                #tt = sendthread._senddata._end
                #if tt > latest:
                    #latest = tt
                    #latestaddr = sendthread._senddata._addr
            end = time.time()

            # mapreduce, work mode. duration = all query completion time
            #duration = end - start
            #NULL='null'
            #latestaddr=[NULL,NULL]
            #sys.stdout.write('%s %s summary %s %.9f %.9f %.9f\n' % (self._myip, latestaddr[0], self._parm[0], duration, start, end))
            #sys.stdout.flush()


    for entry in data:
        intvl, myip, size = entry.split()
        intvl = float(intvl)

        time.sleep(intvl)
        queryall(myip, size).start()

else:
    sys.stderr.write('unknown mode\n')
    sys.stdout.flush()
