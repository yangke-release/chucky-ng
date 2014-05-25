#from embedding.SallyDataDirectoryCreator import SallyDataDirectoryCreator
#from embedding.SallyBasedEmbedder import SallyBasedEmbedder
from conditionAnalyser.FunctionConditions import FunctionConditions
from CustomedPythonEmbedder import Embedder
import os

class ConditionEmbedder:
    feat_dict=dict()
    def __init__(self, outputdir,expcachedir=None):
        
        self.outputdir = outputdir
                
        #self.dataDirCreator = SallyDataDirectoryCreator(self.outputdir,expcachedir)
        #self.embedder = SallyBasedEmbedder()
        self.embedder = Embedder()
    def embed(self, functions, symbolName, symbolType):
        
        funcConditions = []
        li=[]
        flag=False
        
        for i, symbolUser in enumerate(functions):
            # self.logger.info('Processing %s (%s/%s).', symbolUser, i, len(functions))            
            
            x = FunctionConditions(symbolUser)     
            x.setSymbolName(symbolName)
            x.setSymbolType(symbolType)
            feats=x.getFeatures()
            pair=(i,feats)
            funcConditions.append(x)
            li.append(pair)
            #funcConditions.append(x)
            if not flag:
                for feature in feats:
                    flag=True
                    break
                        
        if flag:
            #self.dataDirCreator.create(funcConditions)
            #self.embedder.embed(self.outputdir, 'bin')
            TOC,rTOC=self.TOCrTOC(funcConditions)
            #self.writeToTOC(funcConditions)    
            termDocumentMatrix = self.embedder.embedByList(li)
            return (termDocumentMatrix,TOC,rTOC)
        else:
            return None
        
    def TOCrTOC(self,funcConditions):
        TOC=[str(func.getKey()) for func in funcConditions]
        rTOC=dict()
        for i in xrange(len(TOC)):
            rTOC[TOC[i]]=i
        return (TOC,rTOC)     
    def writeToTOC(self,funcConditions):
        TOCFilename = os.path.join(self.outputdir, 'TOC')
        if not os.path.isdir(self.outputdir):
            os.makedirs(self.outputdir)
        tocFile=open(TOCFilename, 'w')
        for func in funcConditions:
            tocFile.write(str(func.getKey()) + '\n')
        tocFile.close()        
