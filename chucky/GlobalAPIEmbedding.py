
import os
#from joerntools.APIEmbedder import APIEmbedder
from embedding.MemoryAPIEmbedder import APIEmbedder

class GlobalAPIEmbedding():
    def __init__(self, embeddingdir):
        
        self.embeddingdir = embeddingdir
        self.embeddingFilename = 'embedding.libsvm'
        
        if not self._embeddingExists():
            self._createEmbedding()
    
    def _embeddingExists(self):
        return os.path.exists(self.embeddingFilename)
    
    def _createEmbedding(self):
        embedder = APIEmbedder()
        embedder.setOutputDirectory(self.embeddingdir)
        embedder.run()
        
