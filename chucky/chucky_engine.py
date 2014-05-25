from joernInterface.JoernInterface import jutils
import os

import logging
import subprocess
import shutil

from nearestNeighbor.NearestNeighborSelector import NearestNeighborSelector
from ChuckyWorkingEnvironment import ChuckyWorkingEnvironment
from nearestNeighbor.FunctionSelector import FunctionSelector
from conditionAnalyser.ConditionEmbedder import ConditionEmbedder
from GlobalAPIEmbedding import GlobalAPIEmbedding
from AnomalyScoreTool import AnomalyScoreTool
from scipy.sparse import *
EXPR_CACHE_DIR="exprcache"

class ChuckyEngine():

    def __init__(self, basedir):
        self.basedir = basedir
        self.logger = logging.getLogger('chucky')
        
        self.pre_job = None
        jutils.connectToDatabase()
    def _checkAndClearExpCache(self):
	
	if  not self.pre_job:
	    self.clearConditionCache()
	elif not (self.job.symbol ==self.pre_job.symbol):
	    if not (self.job.symbol.target_name==self.pre_job.symbol.target_name and self.job.symbol.target_type=='Callee' and self.pre_job.symbol.target_type=='Callee'):
		self.clearConditionCache()
    
    def clearConditionCache(self):
	expcachedir = os.path.join(self.workingEnv.basedir, EXPR_CACHE_DIR)
	if os.path.isdir(expcachedir):
	    shutil.rmtree(expcachedir) #rm cache             
    def analyze(self, job):

        self.job = job
        self.workingEnv = ChuckyWorkingEnvironment(self.basedir, self.logger)
        self.globalAPIEmbedding = GlobalAPIEmbedding(self.workingEnv.cachedir)
        
        try:            
            nearestNeighbors = self._getKNearestNeighbors()

            #for n in nearestNeighbors:
            #    print n
            
            if nearestNeighbors == []:
                self.logger.warning('Job skipped, no neighbors found')
                self.workingEnv.destroy()
                self.pre_job=self.job
                self.job=None                
                return
            
	    self._checkAndClearExpCache()
	    triple=self._calculateCheckModels(nearestNeighbors)
	    if triple:
		result = self._anomaly_rating(triple)
		self._outputResult(result)
	    else:
		print "Could not find any conditions in all neighbors! Job skiped!"
            self.pre_job=self.job
            self.job=None            
        except subprocess.CalledProcessError as e:
            self.logger.error(e)
            self.logger.error('Do not clean up.')
        else:
            self.logger.debug('Cleaning up.')
            self.workingEnv.destroy()

    """
    Determine the k nearest neighbors for the
    current job.
    """
    def _getKNearestNeighbors(self):
        
        symbol = self.job.getSymbol()
        self.knn = NearestNeighborSelector(self.workingEnv.basedir, self.workingEnv.bagdir)
        self.knn.setK(self.job.n_neighbors)
    
        entitySelector = FunctionSelector()
        symbolUsers = entitySelector.selectFunctionsUsingSymbol(symbol)
        return self.knn.getNearestNeighbors(self.job.function, symbolUsers)
    
    def _calculateCheckModels(self, symbolUsers):
        
        cachedir=None
        if self.job.needcache:
            cachedir = os.path.join(self.workingEnv.basedir, EXPR_CACHE_DIR)
        embedder = ConditionEmbedder(self.workingEnv.exprdir,cachedir)
        symbolName = self.job.getSymbolName()
        symbolType = self.job.getSymbolType()
        return embedder.embed(symbolUsers, symbolName, symbolType)
        
    """
    Determine anomaly score.
    """
    def _anomaly_rating(self,triple):
	rFeatTable=triple[0].index2Term
	matrix=csr_matrix(csc_matrix(triple[0].matrix).T)
	TOC=triple[1]
	rTOC=triple[2]
        atool=AnomalyScoreTool(rFeatTable,matrix,TOC,rTOC)
        result=atool.analyze(str(self.job.function.node_id))
        for score,feat in result:
            self.logger.debug('%+1.5f %s.', float(score), feat)
        return result

    def _outputResult(self, result):
        if len(result)==0:
            self.logger.debug("Condition Mean Vector is Identical with the Condition Vector in considered Function(%s)",str(self.job.function.node_id))
            score=0
            feat="ALL"
        else:
            score, feat = max(result)
        print '{:< 6.5f}\t{:30}\t{:10}\t{}\t{}\t{}\t{}\t{}'.format(score, self.job.function, self.job.function.node_id,self.job.symbol.target_type,self.job.symbol.target_decl_type,self.job.symbol.target_name,feat,self.job.function.location())
    
