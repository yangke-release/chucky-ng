
from joerntools.mlutils.EmbeddingLoader import EmbeddingLoader
from sklearn.metrics.pairwise import pairwise_distances
import sys
MIN_NEIGHBORHOODS_NUM = 2 #including itself
class KNN():
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
        
    def setSimThreshold(self, sim_th):
        self.sim_th = sim_th        
    
    def setNoCache(self, no_cache):
        self.no_cache = no_cache
    
    def initialize(self):
        if not KNN.emb:
            KNN.emb=self._loadEmbedding(self.dirname)
        self.emb = KNN.emb

    def _loadEmbedding(self, dirname):
        #return self.loader.load(dirname, tfidf=False, svd_k=0)
        return self.loader.load(dirname, svd_k=0)
    
    def getNeighborsFor(self, funcId):

        if self.limit:
            validNeighborIds = [funcId] + [x for x in self.limit if x != funcId]
            validNeighbors = [self.emb.rTOC[str(x)] for x in validNeighborIds]
            
            X = self.emb.x[validNeighbors, :]
            D = pairwise_distances(X, metric='cosine')
            longNNI = list(D[0,:].argsort(axis=0))
            NNI = self._checkKNNThresholdModelAndGetNNI(longNNI,D)
            return [validNeighborIds[x] for x in NNI],[D[0,x] for x in NNI]
        else:
            dataPointIndex = self.emb.rTOC[funcId]    
            X = self.emb.x
            D = pairwise_distances(X, metric='cosine')
            longNNI = list(D[dataPointIndex,:].argsort(axis=0))
            NNI = self._checkKNNThresholdModelAndGetNNI(longNNI,D)
            return [self.emb.TOC[x] for x in NNI],[D[dataPointIndex,x] for x in NNI]

    def calculateDistances(self):
        
        self.emb.D = self._calculateDistanceMatrix()
        self._calculateNearestNeighbors()
        
    def _calculateNearestNeighbors(self):
        self.emb.NNI = self.emb.D.argsort(axis=0)
        
    def _calculateDistanceMatrix(self):
        return pairwise_distances(self.emb.x, metric='cosine')
    def _checkKNNThresholdModelAndGetNNI(self,NNI,D):
        if self.k>1:
            if self.k<MIN_NEIGHBORHOODS_NUM:return []
            NNI = NNI[:self.k]
            if 1-D[0,NNI[self.k-1]]<self.sim_th:
                #print 1-D[0,NNI[-1]],self.sim_th
                error_str='KNN skiped. The neighborhood quality does not match the specified top-k similarity threshold.('+str(self.k-1)+'th neighborhood similarity '+str(1-D[0,NNI[-1]])+'< similarity threshold '+str(self.sim_th)+' ).\n'
                sys.stderr.write(error_str)
                return[]
        else:
            index=0
            while(index<len(NNI) and 1-D[0,NNI[index]]>self.sim_th):
                index+=1
            NNI=NNI[:index]
            if(len(NNI)<=MIN_NEIGHBORHOODS_NUM):return []
        return NNI
