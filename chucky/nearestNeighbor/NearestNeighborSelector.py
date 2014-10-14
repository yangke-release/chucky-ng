
import os.path
import time
#from joerntools.KNN import KNN
from CallerKNN import KNN
from joernInterface.nodes.Function import Function

"""
Employs an embedder to first embed a set of entities (e.g., functions)
and then determine the k nearest neighbors to a given entity.
"""
class NearestNeighborSelector:
    
    """
    @param basedir: directory for temporary files. We assume
                    that the cache lives at $basedir/cache
    
    @param embeddingDir: the directory to store the embedding.    
    """
    
    def __init__(self, basedir, embeddingDir,considerCaller=False):
        self.embeddingDir = embeddingDir
        self.k = 10
        self.cachedir = os.path.join(basedir, "cache")
        self.considerCaller=considerCaller
    
    def setK(self, k):
        self.k = k+1
    
    """
    Get nearest neighbors of entity in set of allEntities
    """
    def getNearestNeighbors(self, entity, allEntities):
        
        if len(allEntities) < self.k:
            return []

        return self._nearestNeighbors(entity, self.k, allEntities)
    
    
    def _nearestNeighbors(self, entity, k, allEntities):
        
        
        nodeId = entity.getId()
        limit=[str(e.getId()) for e in allEntities]
        
        knn = KNN()
        knn.setEmbeddingDir(self.cachedir)
        knn.setK(k)
        knn.setLimitArray(limit)
        knn.setCallerConsideration(self.considerCaller)
        knn.initialize()
        #ids = knn.getNeighborsFor(str(nodeId))
        m0,m1,m2,m3,ids = knn.getSimilarContextNeighborsFor(str(nodeId))
        return (m0,m1,m2,m3,[Function(i) for i in ids])
  
    
            
