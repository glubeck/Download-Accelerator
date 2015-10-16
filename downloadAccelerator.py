#!/usr/bin/python

import urllib
import urllib2
import sys, getopt, requests
import threading
import httplib


class downloadThread:
    def __init__(self, index, thread):
        self.index = index
        self.thread = thread


def main(argv):

    global file
    
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

    def readBytes(start, end, request, file):
        request.headers['Range'] = 'bytes=%s-%s' % (start, end)
        f = urllib2.urlopen(request)
        output = f.read()
        file.write(output)
        print "hi"
    
    url =  args[0]

    file = open("file.zip", "w")

    response = requests.head(url)

    contentLength = int(response.headers.get('content-length'))
    rangeLength = contentLength/(numThreads-1)
    remainder = contentLength%(numThreads-1)
    print contentLength
    print rangeLength
    print rangeLength*(numThreads-1) + remainder

    request = urllib2.Request(url)

    threads = []
    i = 0
    while 0 < contentLength:
        if (contentLength/rangeLength) > 0:
            t = threading.Thread(target=readBytes, args=(i, i+rangeLength, request, file,))
            threads.append(t)
            t.start()
            i += rangeLength
            contentLength -= rangeLength
        else:
            remainder = contentLength%100
            t = threading.Thread(target=readBytes, args=(i, i+remainder, request, file,))
            threads.append(t)
            t.start()
            contentLength -= remainder
            break

    
    
if __name__ == "__main__":
   main(sys.argv[1:])
