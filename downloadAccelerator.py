#!/usr/bin/python

import urllib
import urllib2
import sys, getopt, requests
import threading
import httplib
from urlparse import urlparse
import base64


class downloadThread:
    def __init__(self, index, thread):
        self.index = index
        self.thread = thread


def main(argv):

    global numThreads
    global fileName
    global data
    global completed
    
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
            print output
            while completed < numThreads-1:
                with cond:
                    cond.wait()
                
            
            writeToFile()

        
        
    
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

    print contentLength
    
    rangeLength = contentLength/(numThreads-1)
    remainder = contentLength%(numThreads-1)
    

    print contentLength
    
    request = urllib2.Request(url)

    threads = []
    condition = threading.Condition()
    i = 0
    j = 0
    while 0 < contentLength:
        if (contentLength/rangeLength) > 0:
            t = threading.Thread(target=readBytes, args=(i, i+rangeLength-1, request, j, condition,))
            threads.append(t)
            t.start()
            j += 1
            i += rangeLength
            contentLength -= rangeLength
        else:
            remainder = contentLength%100
            t = threading.Thread(target=readBytes, args=(i, i+remainder, request, j, condition,))
            threads.append(t)
            t.start()
            contentLength -= remainder
            break


    
    
if __name__ == "__main__":
   main(sys.argv[1:])
