import json 
import pprint
import numpy as np
import pickle 
import os
from collections import defaultdict 
import urllib2
import pyfoursquare as foursquare

url_head = 'https://api.foursquare.com/v2/venues/search?query='
oauth = '&oauth_token=T0YWZN3QIGS1RNC0HPALM1K1SNR54RZQC2K3WVFUOCIR5EAH&v=20160712'

#'{}&near={}'
root = '/Users/cici/Desktop/DataAnalysis/'

def saveItem(item, fname):
    ''' 
        fname is the absolute path name 
    '''

    with open(fname, 'wb') as fp:
        pickle.dump(item, fp)

def check(dname):
    return True if os.path.exists(dname) else False 

def getUserIds(fname):
    '''
        from batch_requrest get index and user_id map
    '''
    fp = open(fname,'r')
    idMap = {}
    inverseIdMap = {}
    for i, line in enumerate(fp):
        userRecords = json.loads(line)
        user_id = userRecords['id']
        idMap[i] = user_id
        inverseIdMap[user_id] = i 
    return idMap, inverseIdMap

def getDocIds(fname):
    '''
        from batch_requrest get index and history_id map
    '''
    fp = open(fname,'r')
    allDocId = []
    didMap = {}
    inverseDidMap = {}
    for line in fp.readlines():
        userRecords = json.loads(line)
        for item in userRecords['body']['person']['preferences']:
            doc_id = item['documentId']
            if check(os.path.join(root, 'Data', 'crawls', doc_id)):
                allDocId.append(doc_id)
    docId = set(allDocId)
    print len(list(docId))
    for i, did in enumerate(docId):
        didMap[i] = did
        inverseDidMap[did] = i
    return didMap, inverseDidMap

def getDidsByUid(fname):
    '''
        from batch_requrest get user_id with corresponding histories
    '''
    fp = open(fname,'r')
    didbyuid = defaultdict(list)
    for i, line in enumerate(fp):
        userRecords = json.loads(line)
        udoc = []
        for item in userRecords['body']['person']['preferences']:
            doc_id = item['documentId']
            if check(os.path.join(root, 'Data', 'crawls', doc_id)):
                udoc.append(doc_id)
        didbyuid[i] = udoc 

    return didbyuid
    
def getCidsByUid(fname):
    '''
        from batch_requrest get user_id corresponding candidates
    '''

    fp = open(fname, 'r')
    cidbyuid = defaultdict(list)
    for i, line in enumerate(fp) :
        userRecords = json.loads(line)
        cand = userRecords['candidates']
        # filter out none exist files 
        cand = [ x for x in cand if check(os.path.join(root, 'Data', 'crawls', x))]
        # user_id = userRecords['id']
        cidbyuid[i] = cand 
    return cidbyuid

def historyMatrix(fname):
    '''
        input : batch_requrest.json file
        output : ((number of users) x (all_history_docs)) matrix
    '''
    fp = open(fname, 'r')
    data = []
    idMap, inverseIdMap = getUserIds(fname)
    didMap, inverseDidMap = getDocIds(fname)
    ibm = np.zeros((len(idMap), len(didMap)))
    # print ibm.shape
    # pp = pprint.PrettyPrinter(indent = 1)
    for line in fp.readlines():
        userRecords = json.loads(line)
        # pp.pprint(userRecords)
        user_id = userRecords['id']
        for item in userRecords['body']['person']['preferences']:
            if check(os.path.join(root, 'Data', 'crawls', item['documentId'])):
                doc_id = item['documentId']
                rating = item['rating']
                i = inverseIdMap[user_id]
                j = inverseDidMap[doc_id]
                ibm[i,j] = rating

    print ibm.shape 
    saveItem(ibm,'../matrix/utility.pkl')
    # if not os.path.exists('../matrix/utility.pkl'):
    #     fp = open('../matrix/utility.pkl' , 'wb')
    #     pickle.dump(ibm, fp)
    return ibm 


def getCandidateData(qname):
    '''
        from qrel get three lists
        list of user_ids
        list of candidates
        list of ratings
    '''
    qp = open(qname, 'r')
    uList = []
    cList = []
    rList = []
    for line in qp.readlines():
        items = line.strip().split('\t')
        if check(os.path.join(root, 'Data', 'crawls', items[2])):
            uList.append(int(items[0]))
            cList.append(items[2])
            rList.append(int(items[3]))
    return uList, cList, rList

def candidateMatrix(fname, qname):
    '''        
        input : batch_requrest.json and qrel
        output : ((number of users) x (all_candidate_docs)) matrix
        cm : the ground truth of user preferences over candiates 
    '''

    # fp = open(fname, 'r')
    idMap, inverseIdMap = getUserIds(fname)
    
    uList, cList, rList = getCandidateData(qname)
    # print len(dList), len(list(set(dList)))
    nuList = list(set(uList))
    ncList = list(set(cList))
    cm = np.zeros((len(nuList),len(ncList)))
    cMap = {}
    inverseCMap = {}
    for i, item in enumerate(ncList):
        cMap[i] = item
        inverseCMap[item] = i 

    for i, (uid, cid) in enumerate(zip(uList, cList)):
        cm[inverseIdMap[uid],inverseCMap[cid]] = rList[i]

    print cm.shape

    if not os.path.exists('../matrix/canMatrix.pkl'):
        with open('../matrix/canMatrix.pkl','wb') as fp:
            pickle.dump(cm, fp)
            pickle.dump(cMap, fp)
            pickle.dump(inverseCMap, fp)
    return cm, cMap, inverseCMap

def readTRECCS(fn):
    fp = open(fn, 'r')
    #pp = pprint.PrettyPrinter(indent = 4)
    line = fp.read()
    data = json.loads(line)
    item = []
    i = 0
    for key in data.keys():    
        try :
            if 'name' in data[key].keys():
                if type(data[key]['name']) == str:
                    item.append(data[key]['name'])
                else:
                    #assert type(data[key]['name']) == list
                    item.append(data[key]['name'][0])
            if 'categories' in data[key].keys():
                if type(data[key]['name']) == str:
                    item.append(data[key]['categories'])
                else:
                    item.append(data[key]['categories'][0])

            for record in data[key]['reviews_detail']:
                item.append(record['comment'])
                if 'user_location' in record.keys():
                    item.append(record['user_location'])

            result = ' '.join(item)
        except :
            i = i + 1
            print i 
            result = line 
    return result 


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

    client_id = "FUS3H5E15QBVHVE5LCX3SELBQS5CW5ICZVYLGD2X2NFRYY12"
    client_secret = "PIJTOP2415EC3OQRWKKISFUTF5LOX2KP3P2XCXIDW2XHPLID"
    callback = 'http://162.243.84.132'

    # The client id and client secret can be found on your application's Details
   
    auth = foursquare.OAuthHandler(client_id, client_secret, callback)

    #First Redirect the user who wish to authenticate to.
    #It will be create the authorization url for your app
    auth_url = auth.get_authorization_url()
    print 'Please authorize: ' + auth_url
    #If the user accepts, it will be redirected back
    #to your registered REDIRECT_URI.
    #It will give you a code as
    #https://http://xiyulyu.info/?code=CODE
    code = raw_input('The code: ').strip() #'S04QS5AW2H1NVIEM5LOSZFRLXYDV0OYUPTYOMNB4EBABZAHU#_=_'
    #raw_input('The code: ').strip()
    #Now your server will make a request for
    #the access token. You can save this
    #for future access for your app for this user
    access_token = auth.get_access_token(code)
    print 'Your access token is ' + access_token
    #Now let's create an API
    api = foursquare.API(auth)

    for i, line in enumerate(lines): 
        tmp = line.strip().split(',')
        docId, addressId, url, name = tmp 
        query_city = addMap[addressId]
        query_place = name 
        #query = url_head + query_place + '&near=' + query_city + oauth
        #Now you can access the Foursquare API!
        result = api.venues_search(query=query_place, near=query_city, limit = 100)   #ll='-8.063542,-34.872891')
        
        try :
            if len(result[0].categories) > 0 :
                category = result[0].categories[0]
                print(type(str(category)))

        except:
            category = 'none'

        if i % 1000 == 0 :
            print i, result[0].categories
        result.append([category, docId])

    saveItem(result, 'craw_foursquare.pkl')



# https://foursquare.com/oauth2/authenticate
#     ?client_id=DO32UON4HEUVFHBEJKDS1EYJDLQYVGFBRJC2A4WNBZD23CTR&response_type=token
#     &redirect_uri=http://www.taobao.com/
#                   