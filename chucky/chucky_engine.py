from joernInterface.JoernInterface import jutils
import os

import logging
import subprocess
import shutil
import sys

from nearestNeighbor.NearestNeighborSelector import NearestNeighborSelector
from ChuckyWorkingEnvironment import ChuckyWorkingEnvironment
from nearestNeighbor.FunctionSelector import FunctionSelector
from GlobalAPIEmbedding import GlobalAPIEmbedding

from scipy.sparse import *
from conditionAnalyser.FunctionConditions import FunctionConditions
from conditionAnalyser.ConditionPythonEmbedder import Embedder

EXPR_CACHE_DIR="exprcache"

class ChuckyEngine():

    def __init__(self, basedir):
        self.basedir = basedir
        self.logger = logging.getLogger('chucky')
        jutils.connectToDatabase()
	self.embedder=Embedder()	
	
    def analyze(self, job):

        self.job=job
        self.workingEnv = ChuckyWorkingEnvironment(self.basedir, self.logger)
        self.globalAPIEmbedding = GlobalAPIEmbedding(self.workingEnv.cachedir)
        
        try:            
            nearestNeighbors = self._getKNearestNeighbors()

            #for n in nearestNeighbors:
                #print str(n)+"\t"+n.location()
	    dataPointIndex=self.checkNeighborsAndGetIndex(nearestNeighbors)
	    if dataPointIndex is not None:
		termDocumentMatrix=self._calculateCheckModels(nearestNeighbors)
		if termDocumentMatrix:
		    result = self._anomaly_rating(termDocumentMatrix,dataPointIndex)
		    self._outputResult(result)
		else:
		    print "Could not find any conditions in all neighbors! Job skiped!"
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
        
        #symbol = self.job.getSymbol()
        self.knn = NearestNeighborSelector(self.workingEnv.basedir, self.workingEnv.bagdir)
        self.knn.setK(self.job.n_neighbors)
    
        #entitySelector = FunctionSelector()
        #symbolUsers = entitySelector.selectFunctionsUsingSymbol(symbol)
	
	#FIXME:Make additional check for the correctness of job and jobset.For example what if the jobset is None or empty Set.
	jobset=self.job.getJobSet()
	
	if len(jobset) < self.job.n_neighbors+1:
	    self.logger.warning('Job skipped, '+str(len(jobset)-1)+' neighbors found, but '+str(self.job.n_neighbors)+' required')
	    return []
	
	symbolUsers=[]
	for job in jobset:
	    symbolUsers.append(job.function)
	    
        return self.knn.getNearestNeighbors(self.job.function, symbolUsers)
    
    def _calculateCheckModels(self, symbolUsers):
        #symbolName = self.job.getSymbolName()
        #symbolType = self.job.getSymbolType()
	#funcConditions = []
	li=[]
	flag=False
	for i, symbolUser in enumerate(symbolUsers):
	    # self.logger.info('Processing %s (%s/%s).', symbolUser, i, len(functions))            
	    
	    #x = FunctionConditions(symbolUser)     
	    #x.setSymbolName(symbolName)
	    #x.setSymbolType(symbolType)
	    #feats=x.getFeatures()
	    feats=self._getAllSourceFeats(symbolUser,self.job.sourcesinks)
	    #print "------------\n",feats
	    pair=(i,feats)
	    #funcConditions.append(x)
	    li.append(pair)
	    if not flag:
		for feature in feats:
		    flag=True
		    break
			
	if flag:
	    termDocumentMatrix = self.embedder.embed(li)
	    return termDocumentMatrix
	else:
	    return None	
    def _getAllSourceFeats(self,symbolUser,sourcesinks):
	cs=sourcesinks.callee_set
	ps=sourcesinks.parameter_set
	vs=sourcesinks.variable_set
	feats=set()
	if len(cs)>0:
	    for c in cs:
		feats=feats.union(self._getFeats(symbolUser,c.target_name,c.target_type))
	if len(ps)>0:
	    for p in ps:
		feats=feats.union(self._getFeats(symbolUser,p.target_name,p.target_type))	 
	if len(vs)>0:
	    for v in vs:
		feats=feats.union(self._getFeats(symbolUser,v.target_name,v.target_type))
	return feats
	
    def _getFeats(self,symbolUser,symbolName,symbolType):
	x = FunctionConditions(symbolUser)     
	x.setSymbolName(symbolName)
	x.setSymbolType(symbolType)
	feats=x.getFeatures()
	return feats
	
    """
    Determine anomaly score.
    """
    def _anomaly_rating(self,termDocumentMatrix,dataPointIndex):
	self.rFeatTable=termDocumentMatrix.index2Term
	self.x=csr_matrix(csc_matrix(termDocumentMatrix.matrix).T)
	
	mean=self.calculateCenterOfMass(dataPointIndex)
	distance = (mean - self.x[dataPointIndex])
	result=[]
	for feat, score in zip(distance.indices, distance.data):
	    feat_string = self.rFeatTable[feat]
	    self.logger.debug('%+1.5f %s.', float(score), feat_string)
	    result.append((float(score), feat_string))
	return result

    def _outputResult(self, result):
        if len(result)==0:
            self.logger.debug("Condition Mean Vector is Identical with the Condition Vector in considered Function(%s)",str(self.job.function.node_id))
            score=0
            feat="ALL"
        else:
            score, feat = max(result)
        print '{:< 6.5f}\t{:30}\t{:10}\t{}\t{}\t{}'.format(score, self.job.function, self.job.function.node_id,str(self.job.sourcesinks),feat,self.job.function.location())
	
    def calculateCenterOfMass(self, index):
	r,c=self.x.shape
	if r<=1:
	    return None
	else:
	    if index==0:
		X = self.x[1:, :]
	    elif index==r-1:
		X = self.x[:r-1,:]
	    else:
		X = vstack([self.x[:index, :], self.x[index+1:, :]])
	    return csr_matrix(X.mean(axis=0))
    def checkNeighborsAndGetIndex(self,nearestNeighbors):
	if nearestNeighbors == []:
	    #self.logger.warning('Job skipped, no neighbors found')
	    return None
	#ids=[n.node_id for n in nearestNeighbors]
	for i,n in enumerate(nearestNeighbors):
	    if str(self.job.function.node_id)==str(n.node_id):
		return i
	sys.stderr.write('Warning: no data point found for %s\n' % (str(self.job.function.node_id)))
	return None
	    
