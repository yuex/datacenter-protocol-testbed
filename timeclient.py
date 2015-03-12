#!/usr/bin/env python
import socket
import sys
import time
import threading
from utils import *

class timeit(threading.Thread):
    def __init__(self, duration, theThread):
        threading.Thread.__init__(self)
        self._duration = float(duration)
        self._theThread = theThread
        self._finished = threading.Event()
    
    def run(self):
        if self._duration == 0:
            return
        self._finished.wait(self._duration)
        self._theThread.shutdown()

class senddata(threading.Thread):
    def __init__(self, mode, addr, parm):
        threading.Thread.__init__(self)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._addr = addr
        self._mode = mode
        self._parm = parm

        #self._needtosend = size

        self._size = 0
        self._start = 0
        self._end = 0
        self._finished = threading.Event()
    
    def shutdown(self):
        self._end = time.time()
        self._socket.close()
        self._finished.set()

    def run(self):
        self._socket.connect(self._addr)

        self._start = time.time()

        if self._mode == 'query':
            self.querysend()
        elif self._mode == 'size' :
            self.sizesend()
        elif self._mode == 'time':
            self.timesend()
        elif self._mode == 'silent':
            self.silentsend()

        self.shutdown()

    def silentsend(self):
        self._parm = float(self._parm)
        while True:
            if self._finished.isSet():
                break

    def sizesend(self):
        size = int(self._parm)
        
        message = 'end'

        paddinglength = 0
        if size > len(message):
            paddinglength = size - len(message)
        message = '#'*paddinglength + 'end'

        self._size = self._socket.send(magic(message))
    
    def timesend(self):
        self._parm = float(self._parm)
        while True:
            if self._finished.isSet():
                break
            self._size += self._socket.send(magic('#') * BUFFSIZE)
    
    def querysend(self):
        size = int(self._parm)

        message = 'query %s ' % (size)
        
        paddinglength = 0
        if QUERYSIZE > len(message):
            paddinglength = QUERYSIZE - len(message) - 3
        message = message + '#'*paddinglength + 'end'

        self._size = self._socket.send(magic(message))
        
        recvlength = 0
        while True:
            data = self._socket.recv(BUFFSIZE)
            if not data:
                break
            recvlength += len(data)
            if recvlength >= size:
                self._size = recvlength
                break

class timethread(threading.Thread):
    def __init__(self, addr, mode, parm = 0, interval = 0, detail=False):
        threading.Thread.__init__(self)

        self._addr = addr
        self._mode = mode
        self._parm = parm
        self._senddata = senddata(self._mode, self._addr, self._parm)

        self._interval = interval
        self._finished = threading.Event()

        self._prevsize = 0
        self._prevtime = 0

        self._detail = detail
    
    def run(self):
        self._senddata.start()

        if self._mode == 'time' or self._mode == 'silent':
            timeit(self._parm, self._senddata).start()

        if self._interval > 0:
            self._prevtime = time.time()
            while True:
                if self._senddata._finished.isSet():
                    self.task( last=True )
                    self.task( last=True )
                    break
                self.task()
                self._finished.wait(self._interval)

        self._senddata.join()

        start = nicetime(self._senddata._start)
        end = nicetime(self._senddata._end)
        duration = end - start
        size = nicesize(self._senddata._size)
        # size = self._senddata._size
        # sys.stdout.write('%s %.9f %.9f %.9f\n' % (size, duration, start, end))
        if self._detail:
            sys.stdout.write('%s %s %s %.9f %.9f %.9f\n' % (self._addr[0], self._addr[1], size, duration, start, end))
            sys.stdout.flush()
    
    def task(self, last=False):
        if last:
            tempotime = self._senddata._end
        else:
            tempotime = nicetime(time.time())
        intvlsize = self._senddata._size - self._prevsize
        intvltime = tempotime - self._prevtime
        try:
            tempothrouput = nicesize( intvlsize / intvltime )
        except ZeroDivisionError:
            tempothrouput = nicesize( 0 )

        self._prevsize = self._senddata._size
        self._prevtime = tempotime

        transferred = nicesize( self._senddata._size)

        sys.stdout.write("%s %s %.9f %s/s %s\n" % (self._senddata._addr[0], self._senddata._addr[1], tempotime, tempothrouput, transferred))
        sys.stdout.flush()

if __name__ == '__main__':

    if (len(sys.argv) < 5):
        sys.stderr.write("args too few\n")
        sys.exit(1)
    
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    # SIZE = int(sys.argv[3])
    MODE = sys.argv[3]
    #if MODE == 'query':
        #PARM = sys.argv[4:]
    #else:
        #PARM = sys.argv[4]
    PARM = sys.argv[4]

    addr = (HOST, PORT)

    timethread(addr, MODE, PARM, detail=True, interval=1).start()
