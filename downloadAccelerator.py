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
    global stringList
    global fileName
    global lastString

    lastString = []
    stringList = []
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

    def writeToFile(list):
        file = open(fileName, "w")
        
        for k in list:
            file.write(k)

        for l in lastString:
            file.write(l)
            
        file.close()

            
    def readBytes(start, end, request, index):
        request.headers['Range'] = 'bytes=%s-%s' % (start, end)
        #request.headers["Accept-Encoding"] = "identity"
        f = urllib2.urlopen(request, "r")
        output = f.read()
        
        #file = open(fileName, "w")
        #file.write(output)
        #file.close()

        if index < numThreads-1:
            stringList.insert(index, output)
        else:
            lastString.append(output)
        if index == numThreads-2:
            writeToFile(stringList)
        #if index == numThreads-1:
        #    print stringList
        #    writeToFile(stringList)
        
        
    
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

    i = 0
    j = 0
    while 0 < contentLength:
        if (contentLength/rangeLength) > 0:
            t = threading.Thread(target=readBytes, args=(i, i+rangeLength-1, request, j,))
            threads.append(t)
            t.start()
            j += 1
            i += rangeLength
            contentLength -= rangeLength
        else:
            remainder = contentLength%100
            t = threading.Thread(target=readBytes, args=(i, i+remainder, request, j,))
            threads.append(t)
            t.start()
            contentLength -= remainder
            break


    
    
if __name__ == "__main__":
   main(sys.argv[1:])
