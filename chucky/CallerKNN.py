'''
This KNN class implements the KNN algorithm to find k nearest functions for a given function.
It leverage additional function name and file name information and compare caller sets of two functions.
That is, filter name irrelative functions, keep common caller functions.
Here is a simple usage example:


	knn = KNN() 			#Create the object need no parameter (use the following set function to initialize it)
 
        knn.setEmbeddingDir(cachedir)	#Set the directory to cache the API embedding.

        knn.setK(k) 			#Set the number k of nearest neighbors.

        knn.setLimitArray(limit)	#Specify the function name list for which chucky will only calculate for.

        knn.setCallerConsideration(True)#Consider caller information or not. This is the new added feature imported from Ke Yang's paper.
        knn.initialize()		#Initialize the embedding. Check the embedding exists or not. If not then load it. 

	#configuration done

        ids = knn.getNeighborsFor(str(query_function_nodeId)) 
					#Run the KNN algoritm and get the ids of top-k similar functions.
					#The query_function_nodeId will also be return as the the top-1 in the nearest neighborhood list.
***************************************************************
The threshold constants in this file serve for the two new added strategy: 

(1) If the "sematic distance", "function name distance", "file name distance" and "caller set distance" to the query function are all less than the respective "GOOD" threshold.  This function will be rewarded by decreasing the semantic distance by 1. 

(2) If the "function name distance" and the "file name distance" to the query function are both larger than the respective "BAD" distance thresholds, this function will be punished by adding 1 to its semantic distance. 

As the final ranking is based on semantic distance, this function will be elevated or pull down respectively in the top-n(n>=k) list according to these two strategy. More information can be  found in Ke Yang's experimental study: Improving Neighborhood Quality for Chucky: An Experimental Study.
***************************************************************
'''
from joerntools.mlutils.EmbeddingLoader import EmbeddingLoader
from sklearn.metrics.pairwise import pairwise_distances
from joernInterface.nodes.Function import Function
from numpy import matrix
import math
import time
import sys
import re
from scipy.sparse import *
MIN_K=2
#The following constant can be tuned for performance(all >=0 and <=1).

GOOD_SEMANTIC_DISTANCE = 0.618 #0.4:#0.7827:#0.69:0.618
GOOD_CALLER_NAME_DISTANCE = 0.0 #zero means they have just the same  caller set.
GOOD_FUNC_NAME_DISTANCE = 6.0/7.0
GOOD_FILE_NAME_DISTANCE = 0.857143
BAD_FUNC_NAME_DISTANCE = 7.0/8.0
BAD_FILE_NAME_DISTANCE = 3.0/4.0
class KNN():
    caller_map=dict()
    func_name_map=dict()
    file_name_map=dict()
    func_name_distance_map=dict()
    file_name_distance_map=dict()
    caller_name_set_distance_map=dict()
    emb=None
    def __init__(self):
        self.loader = EmbeddingLoader()
    
    def setEmbeddingDir(self, dirname):
        self.dirname = dirname
    
    def setLimitArray(self, limit):
        self.limit = limit
    
    def setK(self, k):
	#When setting k you should coding as:
        #setK(n_neighbors+1)
        # that means k=num_of_neighbors+itself
        #so:k>1 is always satisfied.
	self.k = k
	
    def setCallerConsideration(self, consider):
        self.considerCaller=consider
    def initialize(self):
        if not KNN.emb:
            KNN.emb=self._loadEmbedding(self.dirname)
        self.emb = KNN.emb

    def _loadEmbedding(self, dirname):
        return self.loader.load(dirname, svd_k=0)
    def passNumberCheck(self,csize):
        if csize<self.k:
            sys.stderr.write("Error: candidates num csize:%d<k:%d. please check before call this function.\n" %(csize,self.k))
            return False
	elif self.k<MIN_K:
	    sys.stderr.write("Error: Specified k(=%d) is too small, please given a larger one(k should larger than "+str(MIN_K)+").\n" %(self.k))
	    return False
	else:return True
            
    def getSimilarContextNeighborsFor(self,funcId):
        
        if self.limit:
            validNeighborIds = [funcId] + [x for x in self.limit if x != funcId]
            validNeighbors = [self.emb.rTOC[str(x)] for x in validNeighborIds]
	    csize=len(validNeighborIds)
            if not self.passNumberCheck(csize):
		return (-1,-1,-1,-1,[])
            dataPointIndex=0
            X = self.emb.x[validNeighbors, :]
            return self.calculateDistance(X,validNeighborIds,dataPointIndex,csize,funcId)
        else:
	    csize=self.emb.x.shape[0]
            if not self.passNumberCheck(csize):
		return (-1,-1,-1,-1,[])	    
            dataPointIndex = self.emb.rTOC[funcId]    
            X = self.emb.x
            return self.calculateDistance(X,self.emb.TOC,dataPointIndex,csize,funcId)          
           
    
    def getFuncName(self,fid):
        if str(fid) not in KNN.func_name_map:
            func_name=str(Function(fid))
            KNN.func_name_map[str(fid)]=func_name
        return KNN.func_name_map[str(fid)]
    
    def getFuncFileName(self,fid): 
        if str(fid) not in KNN.file_name_map:
            func=Function(fid)
            location=func.location()
            filename=location.split(':')[0].split('/')[-1]
            KNN.file_name_map[str(fid)]=filename
        return KNN.file_name_map[str(fid)]
    
    def funcNameNGramDistances(self,nids,fid):
        fid=str(fid)
        name=self.getFuncName(fid)
        distances=[]
        for nid in nids:
            nid=str(nid)
            if (fid,nid) in KNN.func_name_distance_map:
                d=KNN.func_name_distance_map[(fid,nid)]
            elif (nid,fid) in KNN.func_name_distance_map:
                d=KNN.func_name_distance_map[(nid,fid)]
            else:
                n_name=self.getFuncName(nid)
                d=self.ngram_jacard_distance(n_name,name)
                KNN.func_name_distance_map[(fid,nid)]=d
            distances.append(d)
        return distances
    
    def fileNameNGramDistances(self,nids,fid):
	fid=str(fid)
        filename=self.getFuncFileName(fid)
	filename_without_suffix=re.sub(r'(\.cpp|\.c|\.h)','',filename)
        distances=[]
        for nid in nids:
	    nid=str(nid)
            if (fid,nid) in KNN.file_name_distance_map:
                d=KNN.file_name_distance_map[(fid,nid)]
            elif (nid,fid) in KNN.file_name_distance_map:
                d=KNN.file_name_distance_map[(nid,fid)]
            else:            
	       nfilename=self.getFuncFileName(nid)
	       nfilename_without_suffix=re.sub(r'(\.cpp|\.c|\.h)','',nfilename)
	       if self.is_suffix_same(nfilename,filename):
		       d=self.ngram_jacard_distance(nfilename_without_suffix,filename_without_suffix)
	       else:d=1
	       KNN.file_name_distance_map[(fid,nid)]=d
            distances.append(d)
        return distances
    
    def is_suffix_same(self,filename1,filename2):
	if '.c' in filename1 and '.c' in filename2:
		return True
	elif '.h' in filename1 and '.h' in filename2:
		return True
	elif '.cpp' in filename1 and '.cpp' in filename2:
		return True
	else: return False
	
    def ngram_jacard_distance(self,s1,s2,ngram=2):
    	s1=s1.lower()
    	s2=s2.lower()
        if len(s1)>len(s2):
            l=len(s2)
        else:l=len(s1)
        if l<=2:
            set1=self.ngram(s1,l)
            set2=self.ngram(s2,l)
        else:
            set1=self.ngram(s1,3)
            set2=self.ngram(s2,3)            
        return 1-float(len(set1&set2))/len(set1|set2)
        
    def ngram(self,s,n=2):
        result=set()
        for i in range(len(s)-n+1):
            result.add(s[i:i+n])
        return result
            
    def calculateDistance(self,X,validNeighborIds,dataPointIndex,high,funcId):
	
        D0 = pairwise_distances(X, metric='cosine')
        NNI = list(D0[dataPointIndex,:].argsort(axis=0))[:int(high)]
        raw_nids=[validNeighborIds[x] for x in NNI]
	
	d1=self.funcNameNGramDistances(raw_nids,funcId)
	d2=self.fileNameNGramDistances(raw_nids,funcId)
	d3=[2 for x in raw_nids]
	
        #merge4D is costly: execution time >1 sec 
        mD=self.merge4D(D0,d1,d2,d3,NNI,dataPointIndex,raw_nids,funcId)
	
        mNNI=mD.argsort(axis=0)
        result =[validNeighborIds[NNI[x]] for x in mNNI[:self.k]]
        result = self.modifyResult(result,D0,d1,d2,d3,mNNI,NNI,dataPointIndex,funcId)
        
        return result
    
    def modifyResult(self,result,D,d1,d2,d3,mNNI,NNI,dataPointIndex,funcId):
        #check and record something
        if str(funcId) not in result:
            result.pop()
            result=[str(funcId)]+result
            nums=[NNI[x] for x in mNNI[:self.k-1]]
            data_d1=[d1[x] for x in mNNI[:self.k-1]]
            data_d2=[d2[x] for x in mNNI[:self.k-1]]
            data_d3=[d3[x] for x in mNNI[:self.k-1]]
        else:
            nums=[NNI[x] for x in mNNI[:self.k] if NNI[x]!=dataPointIndex]
            data1=[d1[x] for x in mNNI[:self.k] if NNI[x]!=dataPointIndex]
            data2=[d2[x] for x in mNNI[:self.k] if NNI[x]!=dataPointIndex]
            data3=[d3[x] for x in mNNI[:self.k] if NNI[x]!=dataPointIndex]
        mean_syntax=D[dataPointIndex,nums].mean(axis=0)
        mean1=sum(data1)/(self.k-1)#func_name
        mean2=sum(data2)/(self.k-1)#file_name
        mean3=sum(data3)/(self.k-1)#caller 
        return (mean_syntax,mean1,mean2,mean3,result)
    
    def merge4D(self,D0,d1,d2,d3,NNI,index,raw_nids,funcId):
        D=D0[index,NNI].copy()
        for i in range(0,len(NNI)):
	    D[i]=D0[index,NNI[i]]
	    if d2[i]==0 and self.considerCaller:
		#They are in a same file.
		if D0[index,NNI[i]]<=GOOD_SEMANTIC_DISTANCE or d1[i]<=GOOD_FUNC_NAME_DISTANCE:
		    #They are semantically similar or similar function name.
		    d=self.caller_name_set_distance_by_id(funcId,raw_nids[i])
		    if d<=GOOD_CALLER_NAME_DISTANCE:
			#They have similar caller set
			D[i]=D0[index,NNI[i]]-1 
	    elif d2[i]>BAD_FILE_NAME_DISTANCE and d1[i]>BAD_FUNC_NAME_DISTANCE:
		#Both function name  and file name are irrelative
		D[i]=D0[index,NNI[i]]+1
        return D 
    
    def getCallers(self,funcId):
        fid=str(funcId)
        if fid not in KNN.caller_map:
            KNN.caller_map[fid]=Function(funcId).callers()
        return KNN.caller_map[fid]
    
    def caller_name_set_distance_by_id(self,id,funcId):
	if (id,funcId) in KNN.caller_name_set_distance_map:
	    distance=KNN.caller_name_set_distance_map[(id,funcId)]
	elif (funcId,id) in KNN.caller_name_set_distance_map:
	    distance=KNN.caller_name_set_distance_map[(funcId,id)]
	else:
	    callers=self.getCallers(funcId)
	    othercallers=self.getCallers(id)
	    if len(callers)==0 or len(othercallers)==0:
	    	if len(callers)+len(othercallers)==0:
		    return 0
		else:return 1
	    else:
	    	distance=self.caller_name_set_distance(callers,othercallers)
	    KNN.caller_name_set_distance_map[(funcId,id)]=distance
	return distance
    
    def caller_name_set_distance(self,callers,othercallers):
	names=set([str(x) for x in callers])
	othernames=set([str(x) for x in othercallers])
	return 1-float(len(names&othernames))/len(names|othernames)
