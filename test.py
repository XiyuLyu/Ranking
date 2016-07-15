from crawls import *
import os, sys
root = '/Users/cici/Desktop/DataAnalysis/'

if len(sys.argv) < 3 : 
    sys.exit(1)
countc = int(sys.argv[1])
istart = int(sys.argv[2])

getCollection(countc, istart)