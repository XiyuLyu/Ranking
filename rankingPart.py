
def evaluateWeightedMean(item, rating):
    rating = normalize(rating)
    sigma = 0.001 
    r =  (np.dot(item, rating) + sigma)/(np.sum(item) + sigma) 
    return r 

def normalize(hdata):
    hdata = hdata/5.0 + 0.2
    return hdata 

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
            predict_uid_cid = evaluateWeightedMean(tmp, rating)
            prediction[uk, can_id] = predict_uid_cid

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



