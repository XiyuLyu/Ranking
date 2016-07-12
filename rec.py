import numpy as np 
import pickle
from parser import * 
from sklearn.feature_extraction.text import  TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import spatial
root = '/Users/cici/Desktop/DataAnalysis/'

def loadUtility():
    fp = open('../matrix/utility.pkl', 'r')
    hdata = pickle.load(fp)
    return hdata 

def loadCanMatrix():
    qp = open('../matrix/canMatrix.pkl','r')    
    cdata = pickle.load(qp)
    cMap = pickle.load(qp)
    inverseCMap = pickle.load(qp)
    return cdata, cMap, inverseCMap  

def normalize(hdata):
    hdata = hdata/5.0 + 0.2
    return hdata 

def historyTFIDF(fname, qname):
    didMap , dummy = getDocIds(fname)
    num_features = 1000
    # tfidf = TfidfVectorizer(max_features = num_features, analyzer = 'word',
                            # ngram_range = (1,3) , stop_words = 'english')
    tfidf = TfidfVectorizer(max_features = num_features, analyzer = 'word', stop_words = 'english')
    history = []
    candidate = []
    dummy, cList, dummy = getCandidateData(qname)
    cList = list(set(cList))
    # count = 0
    for i, v in enumerate(didMap.values()):
        '''
            deal with histories
        ''' 
        fn = os.path.join(root, 'Data', 'crawls', v)
        if os.path.exists(fn):
            contents = open(fn, 'r').read()
            history.append(contents)
            # history.append( readTRECCS(fn) )
    #print history 
    # train_history, val_history = history[:2800], history[2800:]
    # train = tfidf.fit_transform(train_history)
    # val = tfidf.transform(val_history)
    train = tfidf.fit_transform(history)
    saveItem(train,  '../matrix/train_' + str(num_features) + '.pkl')
    # saveItem(train,  '../matrix/val_' + str(num_features) + '.pkl')
    # if not os.path.exists('../matrix/train_100.pkl'):
    #     with open('../matrix/train_100.pkl', 'wb') as fp:
    #         pickle.dump(train, fp)

    print train.shape 

    for i, v in enumerate(cList): 
        '''
            deal with candidates
        '''         

        fn = os.path.join(root, 'Data', 'crawls', v)
        # if i % 100 == 0 :
        #     print i 
        if os.path.exists(fn):
            contents = open(fn, 'r').read()
            candidate.append(contents)
            # candidate.append( readTRECCS(fn) )
    
    test = tfidf.transform(candidate)
    saveItem(test, '../matrix/test_' + str(num_features) + '.pkl')
    # if not os.path.exists('../matrix/test_100.pkl'):
    #     with open('../matrix/test_100.pkl', 'wb') as fp:
    #         pickle.dump(test, fp)

    print test.shape

def adjustedCosine(a, b):
    ua = np.mean(a)
    ub = np.mean(b)
    denominator = np.sqrt(np.dot((a - ua), (a-ua) ) * np.dot((b-ub), (b-ub)) )
    return np.dot((a-ua), (b-ub))/ denominator

def hCSimilarity(train_fn, test_fn, save_fn):
    '''
        calculate History and Candidate matrix similarity
        n x 100 , m x 100 -> n x m 
        #@TODO :
            there are a lot of ways to calcaute similarity
    '''

    fp = open(train_fn, 'r')
    train = pickle.load(fp).toarray()
    fp = open(test_fn , 'r')
    test  = pickle.load(fp).toarray()
    result = np.zeros((len(train), len(test)))

    # for i in range(len(train)):
    #     for j in range(len(test)):
    #         na = np.linalg.norm(train[i,:])
    #         nb = np.linalg.norm(test[i,:])
    #         if na == 0 or nb == 0 :
    #             result[i, j] = 0
    #         else:
    #             #result[i][j] = np.dot(train[i,:], test[j,:])/na/nb
    #             # result[i][j] = cosine_similarity(train[i,:], test[j,:])
    #             result[i][j] = 1 - spatial.distance.cosine(train[i,:], test[j,:])
    result = cosine_similarity(train, test)
    saveItem(result, save_fn)

    # if not os.path.exists('../matrix/item_item_similarity.pkl'):
    #     with open('../matrix/item_item_similarity.pkl', 'wb') as fp:
    #         pickle.dump(result, fp)
def evaluateRankMean(item):
    k = 5 
    return 1 if np.mean(np.sort(item)[::-1][:k]) > 0.5 else 0 

def evaluateByMean(item):
    return 1 if np.mean(item) > 0.5 else 0

def evaluateWeightedMean(item, rating):
    rating = normalize(rating)
    sigma = 0.001 
    # k = 5 
    # topkIndex = np.argsort(item)[::-1][:k] 
    # item = item[topkIndex]
    # rating = rating[topkIndex]
    #print np.dot(item, rating), np.sum(item)
    # return 1 if (np.dot(item, rating) + 0.01)/(np.sum(item) + 0.01) > 0.5 else 0 
    r =  (np.dot(item, rating) + sigma)/(np.sum(item) + sigma) 
    return r 


def rateCan(fname, similarity_fn):
    idMap, inverseIdMap = getUserIds(fname)
    didMap, inverseDidMap = getDocIds(fname)
    cidbyuid = getCidsByUid(fname)
    didbyuid = getDidsByUid(fname)
    with open('../matrix/utility.pkl', 'rb') as fp:
        utility = pickle.load(fp)

    with open('../matrix/canMatrix.pkl','rb') as fp:
        cm = pickle.load(fp)
        cMap = pickle.load(fp) 
        inverseCMap  = pickle.load(fp)

    with open(similarity_fn, 'rb') as fp:
        item_item_similarity = pickle.load(fp)

    prediction = np.zeros(cm.shape)

    tp = 0
    fp = 0

    for uk, uv in idMap.items():
        candidates = cidbyuid[uk]
        preferences = didbyuid[uk]
        preferences_ids = [ inverseDidMap[k] for k in preferences]
        rating = utility[uk, preferences_ids]
        for candidate in candidates:
            can_id = inverseCMap[candidate]
            tmp = item_item_similarity[preferences_ids , can_id]
            # predict_uid_cid = evaluateRankMean(tmp)
            predict_uid_cid = evaluateWeightedMean(tmp, rating)
    #         if predict_uid_cid == 1 and cm[uk, can_id] == 0:
    #             fp = fp + 1
    #         elif predict_uid_cid == 1 and cm[uk, can_id] == 1:
    #             tp = tp + 1
            prediction[uk, can_id] = predict_uid_cid

    # print 'precision is {}'.format(tp * 1.0/(tp + fp))
    saveItem(prediction, os.path.join(root, 'matrix', 'prediction.pkl'))

def rateTopK(k,fname):
    idMap, inverseIdMap = getUserIds(fname)
    with open('../matrix/prediction.pkl','rb') as fp:
        prediction = pickle.load(fp)
    with open('../matrix/canMatrix.pkl','rb') as fp:
        cm = pickle.load(fp)
        cMap = pickle.load(fp) 
        inverseCMap  = pickle.load(fp)
    tp = 0
    fp = 0
    for uk in idMap.keys():
        topk = np.argsort(prediction[uk, :])[::-1][:k]
        print prediction[uk, topk]
        for i in topk:
            if prediction[uk, i] >= 0.5 and cm[uk, i] == 0:
                fp = fp + 1
            elif prediction[uk, i] >= 0.5 and cm[uk, i] == 1:
                tp = tp + 1            
    print 'precision is {}'.format(tp * 1.0/(tp + fp))











