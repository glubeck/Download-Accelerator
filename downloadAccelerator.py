#!/usr/bin/python

import urllib
import urllib2
import sys, getopt, requests

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

    url =  args[0]
    #print threadNum
    #print url

    #print "downloading"
    #urllib.urlretrieve(url, "file.zip")
    

    response = requests.head(url)
    print response.headers
    
if __name__ == "__main__":
   main(sys.argv[1:])
