import os

from joerntools.mlutils.pythonEmbedder.FeatureArray import FeatureArray
from joerntools.mlutils.pythonEmbedder.FeatureArrayToMatrix import FeatureArrayToMatrix

class Embedder:
    def embed(self, li):
           
           featureArray = self.createFeatureArrayByList(li)
           self.termDocMatrix = self._createTermDocumentMatrix(featureArray)
           #self.termDocMatrix.tfidf()
           return self.termDocMatrix
       
    def createFeatureArrayByList(self, li):
            
            featureArray = FeatureArray()
            for label,items in li:
                featureArray.add(label, items)
            return featureArray  
        
    def _createTermDocumentMatrix(self, featureArray):
        converter = FeatureArrayToMatrix()
        return converter.convertFeatureArray(featureArray)
    
    
