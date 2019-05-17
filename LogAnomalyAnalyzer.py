#keep track of how long it takes to run
import time
start = int(time.time())

print('done importing') #it takes a few seconds...

class ErrorBlock:
    def __init__(self):
        self.errs = []
        self.prev = []
        self.features = {}

    def __str__(self):
        errorstring = ""
        for error in self.errs:
            errorstring += str(error.name)+"    "+error[0]+error[1]+"\n"
        return "{}\n{}".format(self.prev,errorstring)
    
    def getFirstErrorIdx(self):
        return self.errs[0].name

    def setPrevLines(self,alldata):
        #get & set as self.prev the last {x} lines before the error block
        endIdx = self.getFirstErrorIdx()
        startIdx = endIdx-10 #10 is just a magic number. you can look as far back as you want from the error block
        if startIdx<0: startIdx = 0 # make start index 0 if it's <0
        self.prev = alldata.iloc[startIdx:endIdx]

    def setFeatures(self,corpus):
        tokens = {k:0 for k in corpus.keys()}
        #for each error in the block
        for error in self.errs:
            #for each word in the error, inc the count
            for word in str(error.MESSAGE).split(' '):
                if word in tokens.keys():
                    tokens[word]+=1
        #for each previous line
        for prev in self.prev.MESSAGE:
            #for each word in the line, inc the count
            for word in str(prev).split(' '):
                if word in tokens.keys():
                    tokens[word]+=1

        self.features = tokens

        #return self for eazy tokenizing with the:
        #"errorblocks = [errblock.setFeatures(corpus) for errblock in errorblocks]"
        #line down below in the main program
        return self
        
        
def getCorpus(errorblocklist):
    corpus = dict()
    #for each errorblock
    for errorblock in errorblocklist:
        #for each error in the block
        for error in errorblock.errs:
            #for each word in the error, add to the corpus or increment the value
            for word in str(error.MESSAGE).split(' '):
                if word in corpus.keys():
                    corpus[word]+=1
                else:
                    corpus[word]=1
        #for each previous line
        for prev in errorblock.prev.MESSAGE:
            #for each word in the line, add to the corpus or increment the value
            for word in str(prev).split(' '):
                if word in corpus.keys():
                    corpus[word]+=1
                else:
                    corpus[word]=1

    #remove things that are obviously not words
    try:
        corpus.pop('')
    except KeyError:
        pass
    try:
        corpus.pop(' ')
    except KeyError:
        pass
    try:
        corpus.pop('"')
    except KeyError:
        pass

    return corpus

#load dataset
import pandas as pd
data_path = "TestData/cleaned_logs_only_alphabet.csv"
data = pd.read_csv(data_path,header=0,encoding='macintosh')

#get all error lines
all_errs = data.loc[(data['LOGCODE'].str.lower().str.contains("e"))&(~data['LOGCODE'].str.lower().str.contains("d"))&(~data['LOGCODE'].str.lower().str.contains("f")) ]

########################################
#get all the error blocks
errorblocks = []

#setup for error blocks
lastidx = all_errs.index[0]
errorblock = ErrorBlock()
errorblock.errs.append(all_errs.loc[lastidx])

for idx in all_errs.index[1:]:
    #if next index is consecutively after the last index we saw, append to error.errorlist
    if idx-lastidx==1: 
        errorblock.errs.append(all_errs.loc[idx]) #append the error we're looking at to the error block
        
    #else, append this errorblock to the errormake then start a new error block
    else:
        errorblock.setPrevLines(data) #get & set previous lines from this error
        errorblocks.append(errorblock)
        errorblock = ErrorBlock()
        errorblock.errs.append(all_errs.loc[idx]) #append the error we're looking at to the error block

    #update the last index we've seen
    lastidx = idx
    
#append the last block
errorblock.setPrevLines(data)
errorblocks.append(errorblock)
########################################

#get corpus for tokens
corpus = getCorpus(errorblocks)

#tokenize error blocks
errorblocks = [errblock.setFeatures(corpus) for errblock in errorblocks]

#get all the feature vectors from the error blocks
x = [list(errblock.features.values()) for errblock in errorblocks]

#normalize data
from sklearn.preprocessing import MinMaxScaler
scaled = MinMaxScaler().fit(x).transform(x)

#find the best features with PCA
from sklearn.decomposition import PCA
pca = PCA(n_components = 2)
scaled = pca.fit_transform(scaled)

#cluster the data and get the number of points in each cluster
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=2).fit(scaled)
import numpy
unique, counts = numpy.unique(kmeans.labels_, return_counts=True)

#get an example from each cluster to display
ex0 = numpy.argwhere(kmeans.labels_ == 0)[0][0]
ex1 = numpy.argwhere(kmeans.labels_ == 1)[0][0]
err0 = errorblocks[ex0]
err1 = errorblocks[ex1]
print("{}\n\n{}".format(err0,err1))

#plot the data
import matplotlib.pyplot as plt
LABEL_COLOR_MAP = {0 : 'green', 1 : 'red'}
color = [LABEL_COLOR_MAP[i] for i in kmeans.labels_]
plt.scatter(scaled[:,0],scaled[:,1],c=color)

#plt.show() is down below

#print info about data set
print("feature size: {}".format(len(scaled[0]))) #corresponds to the n_components in the pca call above
clusterstring = ""
for idx,cluster in enumerate(counts):
    clusterstring += "{} cluster: {}\n".format(LABEL_COLOR_MAP[idx],cluster) #{color} cluster: #

print(clusterstring)
end = int(time.time())
print("took {} seconds".format(end-start)) #time it took to run the program

#show the plot
plt.title(clusterstring)
plt.xlabel("principal component 1")
plt.ylabel("principal component 2")
plt.show()
