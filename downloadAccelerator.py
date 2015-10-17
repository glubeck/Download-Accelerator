#!/usr/bin/python

import urllib2
import sys, getopt, requests
import threading
import httplib
import timeit
from urlparse import urlparse

def main(argv):

    global numThreads
    global fileName
    global data
    global completed
    global stop
    global begin
    global url
    global numOfBytes
    
    completed = 0    
    data = {}
    numThreads = 0
    url = ''
    
    try:
        opts, args = getopt.getopt(argv,"n:")
    except getopt.GetoptError:
        print '-n threads'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-n':
            numThreads = int(arg)

            
    def writeToFile():
        file = open(fileName, "w")
        for k in range(numThreads):
            temp = data[k]
            file.write(temp)
        file.close()
        global stop
        stop = timeit.default_timer()        
        print url + " " + str(numThreads) + " " + str(numOfBytes) + " " + str(stop-begin)
        
    def readBytes(start, end, request, index, cond):
        request.headers['Range'] = 'bytes=%s-%s' % (start, end)
        f = urllib2.urlopen(request, "r")
        output = f.read()
        data[index] = output
        
        if index < numThreads-1:
            global completed
            completed += 1
            with cond:
                cond.notifyAll()
        
        if index == numThreads-1:
            while completed < numThreads-1:
                with cond:
                    cond.wait()
                
            writeToFile()

    def readBytesNoParallel(start, end, request):
        
        request.headers['Range'] = 'bytes=%s-%s' % (start, end)
        f = urllib2.urlopen(request, "r")
        output = f.read()
        file = open(fileName, "w")
        file.write(output)
        file.close()
        global begin
        stop = timeit.default_timer()
        print url + " " + str(numThreads) + " " + str(numOfBytes) + " " + str(stop-begin)
        
    
    url =  args[0]

    fileName = url.rsplit('/',1)[-1]

    if fileName == "":
        fileName = "index.html"
    
    
    parsedURL = urlparse(url)
    
    conn = httplib.HTTPConnection(parsedURL.netloc, 80)
    path = parsedURL.path
    if len(path) is 0:
        path = '/'
    conn.request('HEAD', path)
    res = conn.getresponse()
    header = res.getheader('Content-Length')
    contentLength = int(header)
    numOfBytes = contentLength
    rangeLength = 0
    remainder = 0
    if numThreads > 1:
        rangeLength = contentLength/numThreads
        remainder = rangeLength + (contentLength%numThreads)
        
    request = urllib2.Request(url)
    
    condition = threading.Condition()
    i = 0
    j = 0
    global begin
    begin = timeit.default_timer()
    
    while 0 < contentLength:
        if numThreads == 1:
            t = threading.Thread(target=readBytesNoParallel, args=(0, contentLength, request,))
            t.start()
            break
        elif (contentLength/rangeLength) > 1:
            t = threading.Thread(target=readBytes, args=(i, i+rangeLength-1, request, j, condition,))
            t.start()
            j += 1
            i += rangeLength
            contentLength -= rangeLength
    
        elif contentLength/rangeLength == 1:
            t = threading.Thread(target=readBytes, args=(i, i+remainder, request, j, condition,))
            t.start()
            contentLength -= remainder
            break

    
if __name__ == "__main__":
   main(sys.argv[1:])
