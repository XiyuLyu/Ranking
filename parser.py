import json 
import pprint
import numpy as np
import pickle 
import os
from collections import defaultdict 
import urllib
from datetime import date

def getContexts():
    fn = os.path.join(root, 'Data', 'contexts2015.csv')
    addMap = {}
    lines = open(fn, 'r').readlines()
    for line in lines : 
        tmp = line.strip().split(',')
        addMap[tmp[0]] = ','.join(tmp[1:])

    return addMap

def getCollection():
    addMap = getContexts()
    fn = os.path.join(root, 'Data', 'collection_2015.csv')
    lines = open(fn, 'r').readlines()

    result = []
    error = []

    client_id = "FUS3H5E15QBVHVE5LCX3SELBQS5CW5ICZVYLGD2X2NFRYY12"
    client_secret = "PIJTOP2415EC3OQRWKKISFUTF5LOX2KP3P2XCXIDW2XHPLID"
    # callback = 'http://162.243.84.132'
    callback = ''
    today= date.today()
    v = today.strftime('%Y%m%d')
    cnr = []
    for i, line in enumerate(lines): 
        tmp = line.strip().split(',')
        if len(tmp) == 4:
            docId, addressId, url, name = tmp
        elif len(tmp) > 4:
            docId, addressId, url, name = tmp[:4]
        else:
            continue
        cnr.append()
        query = name 
        near = addMap[addressId]
        countc = 0
        countnc = 0
        print i
        if 'foursquare' not in url:
            q = 'https://api.foursquare.com/v2/venues/search' +\
                    '?client_id=' + client_id + \
                    '&client_secret=' + client_secret +\
                    '&v=' + v +\
                    '&near=' + near +\
                    '&query=' + query
            resp = urllib.urlopen(q)
            page = json.loads(resp.read())

            try :
                countc = countc + 1
                ctg = page['response']['venues'][0]['categories']
                result.append([ctg, docId]) 
                if countc % 4000 == 0 :
                    print countc, ctg
                    saveItem(result,'result_of_category{}_{}.pkl'.format(countc,i))
            except :
                countnc = countnc + 1
                ctg = ''
                error.append([docId, url])
                if countnc % 1000 ==0:
                    saveItem(error,'error_of_category{}_{}.pkl'.format(countnc,i))
        if i == 500:
            break
                  