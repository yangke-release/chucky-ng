
import subprocess
import shlex
import os.path

from nearestNeighbor.APISymbolEmbedder import APISymbolEmbedder
from joernInterface.nodes.Function import Function
from ChuckyKnnTool import ChuckyKnnTool
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
    
    def __init__(self, basedir, embeddingDir):
        self.embeddingDir = embeddingDir
        self.k = 10
        cachedir = os.path.join(basedir, "cache")
        
        self.embedder = APISymbolEmbedder(cachedir, embeddingDir)
        
    
    def setEmbedder(self, embedder):
        self.embedder = embedder
    
    
    def setK(self, k):
        self.k = k
    
    """
    Get nearest neighbors of entity in set of allEntities
    """
    def getNearestNeighbors(self, entity, allEntities):
        
        if len(allEntities) < self.k:
            return []

        self.embedder.embed(allEntities)
        return self._nearestNeighbors(entity, self.k)
    
    # FIXME: knn.py offers a python-class so we don't 
    # have to make a call via the shell here
    
    def _nearestNeighbors(self, entity, k):
        
        nodeId = entity.getId()
        knn=ChuckyKnnTool()
        neighbor_ids=knn.getknn(nodeId,self.embeddingDir,k)
        neighbors=[]
        for neighbor in neighbor_ids:
            neighbors.append(Function(neighbor))
        return neighbors      
  
