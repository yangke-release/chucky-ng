
from joerntools.mlutils.EmbeddingLoader import EmbeddingLoader
from sklearn.metrics.pairwise import pairwise_distances


class KNN():
    emb=None
    def __init__(self):
        self.loader = EmbeddingLoader()
    
    def setEmbeddingDir(self, dirname):
        self.dirname = dirname
    
    def setLimitArray(self, limit):
        self.limit = limit
    
    def setK(self, k):
        self.k = k
    
    def initialize(self):
        if not KNN.emb:
            KNN.emb=self._loadEmbedding(self.dirname)
        self.emb = KNN.emb

    def _loadEmbedding(self, dirname):
        #return self.loader.load(dirname, tfidf=False, svd_k=0)
        return self.loader.load(dirname, svd_k=0)
    
    def getNeighborsFor(self, funcId):
        
        nReturned = 0

        if self.limit:
            validNeighborIds = [funcId] + [x for x in self.limit if x != funcId]
            validNeighbors = [self.emb.rTOC[str(x)] for x in validNeighborIds]
            
            X = self.emb.x[validNeighbors, :]
            D = pairwise_distances(X, metric='cosine')
            NNI = list(D[0,:].argsort(axis=0))[:self.k]
            return [validNeighborIds[x] for x in NNI]
        else:
            dataPointIndex = self.emb.rTOC[funcId]    
            X = self.emb.x
            D = pairwise_distances(X, metric='cosine')
            NNI = list(D[dataPointIndex,:].argsort(axis=0))[:self.k]
            return [self.emb.TOC[x] for x in NNI]

    def calculateDistances(self):
        
        self.emb.D = self._calculateDistanceMatrix()
        self._calculateNearestNeighbors()
        
    def _calculateNearestNeighbors(self):
        self.emb.NNI = self.emb.D.argsort(axis=0)
        
    def _calculateDistanceMatrix(self):
        return pairwise_distances(self.emb.x, metric='cosine')
