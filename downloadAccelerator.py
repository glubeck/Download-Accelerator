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
    threadNum = 0
    url = ''
    try:
        opts, args = getopt.getopt(argv,"n:")
    except getopt.GetoptError:
        print '-n threads'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-n':
            threadNum = arg

    def readBytes(start, end, request, file):
        request.headers['Range'] = 'bytes=%s-%s' % (start, end)
        f = urllib2.urlopen(request)
        output = f.read()
        file = open("file.zip", "w")
        file.write(output)
        file.close()
        print "hi"
    
    url =  args[0]

    response = requests.head(url)

    contentLength = int(response.headers.get('content-length'))
    print contentLength

    request = urllib2.Request(url)

    

    threads = []
    i = 0
    while 0 < contentLength:
        if (contentLength/100) > 0:
            t = threading.Thread(target=readBytes, args=(i, i+99, request, file,))
            threads.append(t)
            t.start()
            i += 100
            contentLength -= 100
        else:
            remainder = contentLength%100
            print i + remainder
            
            #t = threading.Thread(target=readBytes, args=(i, i+remainder-1, request, file,))
            #threads.append(t)
            #t.start()
            break

    
        
    
    
    
if __name__ == "__main__":
   main(sys.argv[1:])
