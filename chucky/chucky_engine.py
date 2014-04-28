from joernInterface.JoernInterface import jutils

import logging
import subprocess
import os
import shutil
from nearestNeighbor.NearestNeighborSelector import NearestNeighborSelector
from ChuckyWorkingEnvironment import ChuckyWorkingEnvironment
from nearestNeighbor.FunctionSelector import FunctionSelector
from conditionAnalyser.ConditionEmbedder import ConditionEmbedder
from AnomalyScoreTool import AnomalyScoreTool

EXPR_CACHE_DIR="exprcache"

class ChuckyEngine():

    def __init__(self, basedir):
        self.basedir = basedir
        self.logger = logging.getLogger('chucky')
        
        self.pre_job = None
        jutils.connectToDatabase()
        
    def _checkAndClearExpCache(self):
        if (not self.pre_job) or not (self.job.symbol ==self.pre_job.symbol):
            cachedir = os.path.join(self.workingEnv.basedir, EXPR_CACHE_DIR)
            if os.path.isdir(cachedir):
                shutil.rmtree(cachedir) #rm cache
                #os.makedirs(cachedir)#create an empty one 

    def analyze(self, job):

        self.job = job
        self.workingEnv = ChuckyWorkingEnvironment(self.basedir, self.logger)
        
        try:            
            nearestNeighbors = self._getKNearestNeighbors()
            
            if nearestNeighbors == []:
                self.logger.warning('Job skipped, no neighbors found')
                self.workingEnv.destroy()
                return
            self._checkAndClearExpCache()
            if self._calculateCheckModels(nearestNeighbors):
                result = self._anomaly_rating()
            else:
                result=[]
            self._outputResult(result)

        except subprocess.CalledProcessError as e:
            self.logger.error(e)
            self.logger.error('Do not clean up.')
        else:
            self.pre_job=self.job
            self.job=None            
            self.logger.debug('Cleaning up.')
            self.workingEnv.destroy()

    """
    Determine the k nearest neighbors for the
    current job.
    """
    def _getKNearestNeighbors(self):
        symbol = self.job.getSymbol()
        entitySelector = FunctionSelector()
        if (not self.pre_job) or (not self.symbolUsers) or not (self.job.symbol ==self.pre_job.symbol):           
            self.symbolUsers = entitySelector.selectFunctionsUsingSymbol(symbol) 
        self.knn = NearestNeighborSelector(self.workingEnv.basedir, self.workingEnv.bagdir)
        self.knn.setK(self.job.n_neighbors)
        return self.knn.getNearestNeighbors(self.job.function, self.symbolUsers)
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
    def _anomaly_rating(self):
        tool=AnomalyScoreTool();
        li=tool.analyze(str(self.job.function.node_id),self.workingEnv.exprdir)
        results = []
        for line in li:
            score, feat = line.split(' ', 1)
            results.append((float(score), feat))
            self.logger.debug('%+1.5f %s.', float(score), feat)
        return results

    def _outputResult(self, result):
        if len(result)==0:
            self.logger.debug("Condition Mean Vector is Identical with the Condition Vector in considered Function(%s)",str(self.job.function.node_id))
            score=0
            feat="ALL"
        else:
            score, feat = max(result)
        print '{:< 6.5f}\t{:40}\t{:10}\t{:10}\t{:10}\t{:10}\t{}\t{}'.format(score, self.job.function, self.job.function.node_id,self.job.symbol.target_type,self.job.symbol.target_decl_type,
            self.job.symbol.target_name, feat,self.job.function.location())
    

