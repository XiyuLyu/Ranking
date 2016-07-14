import json 
import pprint
import numpy as np
import pickle 
import os
from collections import defaultdict 
import urllib
from datetime import date
root = '/Users/cici/Desktop/DataAnalysis/'


def saveItem(item, fname):
    with open(fname, 'wb') as fp:
        pickle.dump(item, fp)


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
    fn = os.path.join(root, 'Data', 'new_collection_part1.csv')
    lines = open(fn, 'r').readlines()

    result = []
    error = []

    # client_id = "FUS3H5E15QBVHVE5LCX3SELBQS5CW5ICZVYLGD2X2NFRYY12"
    # client_secret = "PIJTOP2415EC3OQRWKKISFUTF5LOX2KP3P2XCXIDW2XHPLID"
    client_id = 'DO32UON4HEUVFHBEJKDS1EYJDLQYVGFBRJC2A4WNBZD23CTR'
    client_secret = 'PW0P0000UVQSTWLIZLNLSD1MDAPKIUAGQMW101GRUZ42O1OJ'

    # callback = 'http://162.243.84.132'
    callback = ''
    today= date.today()
    v = today.strftime('%Y%m%d')
    cnr = []        
    countc = 0
    countnc = 0
    for i, line in enumerate(lines):
        # print i 
        tmp = line.strip().split(',')
        if len(tmp) == 4:
            docId, addressId, url, name = tmp
        elif len(tmp) > 4:
            docId, addressId, url, name = tmp[:4]
        else:
            continue
        query = name 
        near = addMap[addressId]

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
                ctg = page
                countc = countc + 1
                result.append([ctg, docId]) 
                #print ctg , docId
                # print i
                if countc % 100 == 0 :
                    print i
                if countc % 4000 == 0 :
                    print countc, ctg
                    saveItem(result,'result_of_category{}_{}.pkl'.format(countc,i))
                    saveItem(error,'error_of_category{}_{}.pkl'.format(countnc,i))
                    result = []
                    error = []
                    
            except :
                # print i
                countnc = countnc + 1
                ctg = ''
                error.append([docId, url])
                # if countnc % 1000 ==0:
                #     saveItem(error,'error_of_category{}_{}.pkl'.format(countnc,i))

                  