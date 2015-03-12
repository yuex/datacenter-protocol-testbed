#!/usr/bin/env python
import getopt
import socket
import sys
import threading
import time
from utils import *
from timeclient import *

class recvdata(threading.Thread):
    def    __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self._conn = conn
        self._addr = addr

        self._size = 0
        self._start = 0
        self._end = 0

        self._finished = threading.Event()
    
    def shutdown(self):
        self._end = time.time()
        self._conn.close()
        self._finished.set()
    
    def run(self):
        self._start = time.time()

        size = 0
        while True:
            data = self._conn.recv(BUFFSIZE)
            if not data:
                break

            self._size += len(data)

            #if data.find(magic('query ')) >= 0:
            if data[:6] == 'query ':
                size = int(data[6:6+data[6:].find(' ')])

            if data[-3:] == 'end':
                if size > 0:
                    self._conn.send(magic('#'*size))
                break

        self.shutdown()

class thdserverthread(threading.Thread):
    def __init__(self, conn, addr, interval=0):
        threading.Thread.__init__(self)
        self._recvdata = recvdata(conn, addr)

        self._interval = interval
        self._finished = threading.Event()
        
        self._prevsize = -1
        self._prevtime = -1

    def shutdown(self):
        self._recvdata.shutdown()
    
    def run(self):
        self._recvdata.start()

        if self._interval > 0:
            while True:
                self._finished.wait(self._interval)
                if self.task():
                    break

        self._recvdata.join()

        start = nicetime(self._recvdata._start)
        end = nicetime(self._recvdata._end)
        duration = end - start
        size = nicesize(self._recvdata._size)
        # size = self._recvdata._size

        #sys.stdout.write('%s %s\n' % self._recvdata._addr)
        if self._interval == 0:
            sys.stdout.write('%s %s %s %.9f %.9f %.9f\n' % (self._recvdata._addr[0], self._recvdata._addr[1], size, duration, start, end))
        sys.stdout.flush()
    
    def task(self):
        tempotime = time.time()
        first = False
        last = False

        if self._prevtime < 0:
            self._prevtime = self._recvdata._start
            first = True
        if self._recvdata._finished.isSet():
            tempotime = self._recvdata._end
            last = True

        intvlsize = self._recvdata._size - self._prevsize
        intvltime = tempotime - self._prevtime

        try:
            tempothrouput = intvlsize / intvltime
        except ZeroDivisionError:
            tempothrouput = 0

        self._prevsize = self._recvdata._size
        self._prevtime = tempotime

        tempotime = nicetime(tempotime)
        tempothrouput = nicesize(tempothrouput)
        transferred = nicesize(self._recvdata._size)

        if first:
            sys.stdout.write("%s %s %.9f %s/s %s\n" % (self._recvdata._addr[0], self._recvdata._addr[1], tempotime, nicesize(0), nicesize(0)))
        sys.stdout.write("%s %s %.9f %s/s %s\n" % (self._recvdata._addr[0], self._recvdata._addr[1], tempotime, tempothrouput, transferred))
        if last:
            sys.stdout.write("%s %s %.9f %s/s %s\n" % (self._recvdata._addr[0], self._recvdata._addr[1], tempotime, nicesize(0), transferred))

        sys.stdout.flush()

        return last

if __name__ == '__main__':

    #opts, argv = getopt.getopt(sys.argv[1:], 'tu')

    if (len(sys.argv) < 1):
        sys.stderr.write("args too few\n")
        sys.exit(1)

    SOCKTYPE = socket.SOCK_STREAM
    #for opt, val in opts:
        #if opt == '-t':
            #SOCKTYPE = socket.SOCK_STREAM
        #elif opt == '-u':    # udp doesn't use listen(), feature uncomplete
            #SOCKTYPE = socket.SOCK_DGRAM

    HOST = ''
    PORT = int(sys.argv[1])
    INTVL = 0
    if len(sys.argv) >= 3:
        INTVL = float(sys.argv[2])

    s = socket.socket(socket.AF_INET, SOCKTYPE)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(BACKLOG)

    while True:
        conn, addr = s.accept()
        t = thdserverthread(conn, addr, INTVL)
        t.start()
