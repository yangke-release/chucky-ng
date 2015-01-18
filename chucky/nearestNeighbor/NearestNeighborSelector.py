
import os.path
#from joerntools.KNN import KNN
from CallerKNN import KNN
from joernInterface.nodes.Function import Function
DEFAULT_K=10
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
        self.k = DEFAULT_K
        self.cachedir = os.path.join(basedir, "cache")
        self.considerCaller=considerCaller
    
    def setK(self, k):
        self.k = k+1#n_neighbors+itself   
    """
    Get nearest neighbors of entity in set of allEntities
    """
    def getNearestNeighbors(self, entity, allEntities):
        
        if len(allEntities) < self.k:
            return []
        
        
        nodeId = entity.getId()
        
        limit=[str(e.getId()) for e in allEntities]
        
        knn = KNN()
        knn.setEmbeddingDir(self.cachedir)
        knn.setK(self.k)
        knn.setLimitArray(limit)
        knn.setCallerConsideration(self.considerCaller)
        knn.initialize()
        
        #ids = knn.getNeighborsFor(str(nodeId))
        #if not ids or ids==[]:return []
        #elif str(nodeId) not in ids:
            #ids.pop()
            #ids=[str(nodeId)]+ids
        #return [Function(i) for i in ids]
        #ids = knn.getNeighborsFor(str(nodeId))
        m0,m1,m2,m3,ids = knn.getSimilarContextNeighborsFor(str(nodeId))
        #mean_syntax,mean_fun_name,mean_file_name,mean_caller
        return (m0,m1,m2,m3,[Function(i) for i in ids])        
    
    '''
    def _createLimitFile(self, entities):
        filename = os.path.join(self.cachedir, 'limitfile')
        f = file(filename, 'w')
        f.writelines([str(e.getId()) + '\n' for e in entities] )
        f.close()
        return filename
    '''
            
