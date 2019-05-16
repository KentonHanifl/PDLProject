import pandas as pd
from sklearn.cluster import KMeans

print('starting')

class ErrorBlock:
    def __init__(self):
        self.errs = []
        self.prev = []

        self.features = {}

    def __str__(self):
        return "{}\n\n{}".format(self.errs.__str__(),self.prev.__str__())

    def getFirstErrorIdx(self):
        return self.errs[0].name

    def setPrevLines(self,alldata):
        endIdx = self.getFirstErrorIdx()
        startIdx = endIdx-10 
        if startIdx<0: startIdx = 0
        self.prev = alldata.iloc[startIdx:endIdx]

    def setFeatures(self,corpus):
        
        tokens = {k:0 for k in corpus.keys()}
        #for each error in the block
        for error in self.errs:
            #for each word in the error, inc the count
            for word in error.MESSAGE.split(' '):
                if word in tokens.keys():
                    tokens[word]+=1
        #for each previous line
        for prev in self.prev.MESSAGE:
            #for each word in the line, inc the count
            for word in prev.split(' '):
                if word in tokens.keys():
                    tokens[word]+=1

        self.features = tokens
        return self
        
        
def getCorpus(errorblocklist):
    corpus = dict()
    #for each errorblock
    for errorblock in errorblocklist:
        #for each error in the block
        for error in errorblock.errs:
            #for each word in the error, add to the corpus or increment the value
            for word in error.MESSAGE.split(' '):
                if word in corpus.keys():
                    corpus[word]+=1
                else:
                    corpus[word]=1
        #for each previous line
        for prev in errorblock.prev.MESSAGE:
            #for each word in the line, add to the corpus or increment the value
            for word in prev.split(' '):
                if word == 'LOGCODE': print("fuck")
                if word in corpus.keys():
                    corpus[word]+=1
                else:
                    corpus[word]=1
    corpus.pop('')
    corpus.pop('"')
    return corpus
#load dataset
data = pd.read_csv("reformat.csv",header=0,encoding='macintosh')
#get all error lines
all_errs = data.loc[(data['LOGCODE'].str.lower().str.contains("e"))&(~data['LOGCODE'].str.lower().str.contains("d"))&(~data['LOGCODE'].str.lower().str.contains("f")) ]

###get all the error blocks
errorblocks = []

#setup for error blocks
lastidx = all_errs.index[0]
errorblock = ErrorBlock()
errorblock.errs.append(all_errs.loc[lastidx])

for idx in all_errs.index[1:]:
    #if next index is consecutive append to error.errorlist
    if idx-lastidx==1: 
        errorblock.errs.append(all_errs.loc[idx])
        
    #else, append this errorblock to the errormake a new error
    else:
        errorblock.setPrevLines(data) #get previous lines
        errorblocks.append(errorblock)
        errorblock = ErrorBlock()
        errorblock.errs.append(all_errs.loc[idx])
        
    lastidx = idx
#append the last block
errorblock.setPrevLines(data)
errorblocks.append(errorblock)

corpus = getCorpus(errorblocks)
errorblocks = [errblock.setFeatures(corpus) for errblock in errorblocks]
x = [list(errblock.features.values()) for errblock in errorblocks]

kmeans = KMeans(n_clusters=2,random_state=0).fit(x)

print(kmeans.labels_



###### template
##y = []
##for c in range(n_classes):
##    it = c*8
##    cls = pcatrans[n_samples*c:n_samples*(c+1)]
##    kmeans = KMeans(n_clusters=8, random_state=0).fit(cls)
##    labels = kmeans.labels_
##    labels = [label+it for label in labels]
##    y+=labels



####for formatting the csv, but this doesn't work well
##csv=False
##if csv:
##    f = open("reformat.csv",'rb')
##    d = f.readlines()
##    f.close()
##    for idx,line in enumerate(d):
##        d[idx] = line.replace(b",",b' ').rstrip(b",")
##    f = open("reformat.csv",'wb')
##    f.writelines(d)
##    f.close()
