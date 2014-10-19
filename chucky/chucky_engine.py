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

from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import pairwise_distances
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
            m0,m1,m2,m3,nearestNeighbors = self._getKNearestNeighbors()
	    #mean_syntax,mean_fun_name,mean_file_name,mean_caller
	    
            #for n in nearestNeighbors:
            #    print str(n)+"\t"+n.location()
	    
	    dataPointIndex=self.checkNeighborsAndGetIndex(nearestNeighbors)
	    if dataPointIndex is not None:
		termDocumentMatrix=self._calculateCheckModels(nearestNeighbors)
		if termDocumentMatrix:
		    mcc,ccm,result = self._anomaly_rating(termDocumentMatrix,dataPointIndex)
		    self._outputResult(m0,m1,m2,m3,mcc,ccm,result)
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
        
        symbol = self.job.getSymbol()
	considerCaller=False
	if symbol.target_type=="Parameter":
	    considerCaller=True	
        self.knn = NearestNeighborSelector(self.workingEnv.basedir, self.workingEnv.bagdir,considerCaller)
        self.knn.setK(self.job.n_neighbors)
    
        entitySelector = FunctionSelector()
        symbolUsers = entitySelector.selectFunctionsUsingSymbol(symbol)
	return self.knn.getNearestNeighbors(self.job.function, symbolUsers)
    
    def _calculateCheckModels(self, symbolUsers):
        symbolName = self.job.getSymbolName()
        symbolType = self.job.getSymbolType()
	funcConditions = []
	li=[]
	flag=False
	
	for i, symbolUser in enumerate(symbolUsers):
	    # self.logger.info('Processing %s (%s/%s).', symbolUser, i, len(functions))            
	    
	    x = FunctionConditions(symbolUser)     
	    x.setSymbolName(symbolName)
	    x.setSymbolType(symbolType)
	    feats=x.getFeatures()
	    pair=(i,feats)
	    funcConditions.append(x)
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
        
    """
    Determine anomaly score.
    """
    def _anomaly_rating(self,termDocumentMatrix,dataPointIndex):
	self.rFeatTable=termDocumentMatrix.index2Term
	self.x=csr_matrix(csc_matrix(termDocumentMatrix.matrix).T)
	
	mean=self.calculateCenterOfMass(dataPointIndex)
	
	mean_cos_distance=self.meancos(dataPointIndex)
	tm=vstack([mean,self.x[dataPointIndex,:]])
	d=pairwise_distances(tm,metric="cosine")
	cos_distance_with_mean=d[1,0]
		
	distance = (mean - self.x[dataPointIndex])
	result=[]
	for feat, score in zip(distance.indices, distance.data):
	    feat_string = self.rFeatTable[feat]
	    self.logger.debug('%+1.5f %s.', float(score), feat_string)
	    result.append((float(score), feat_string))
	    
	return mean_cos_distance,cos_distance_with_mean,result

    def _outputResult(self,m0,m1,m2,m3,mcc,ccm, result):
        
        #score, feat = max(result)
	length=len(result)
	if length==0:
	    self.logger.debug("Condition Mean Vector is Identical with the Condition Vector in considered Function(%s)",str(self.job.function.node_id))
	    score=0
	    feat="ALL"
	    spec=0
	else:
	    s1=0.0
	    for t in result:
		s1+=t[0]
	    score, feat= max(result)
	    if length==1:
		spec=0
	    else:
		spec=score-(s1-score)/(length-1)        
        print '{:< 6.5f}\t{:30}\t{:10}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(score, self.job.function, self.job.function.node_id,self.job.symbol.target_type,self.job.symbol.target_decl_type,self.job.symbol.target_name,feat,m0,m1,m2,m3,mcc,ccm,spec,self.job.function.location())
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
	    self.logger.warning('Job skipped, no neighbors found')
	    return None
	#ids=[n.node_id for n in nearestNeighbors]
	for i,n in enumerate(nearestNeighbors):
	    if str(self.job.function.node_id)==str(n.node_id):
		return i
	sys.stderr.write('Warning: no data point found for %s\n' % (str(self.job.function.node_id)))
	return None
    
    def meancos(self,index):
	r,c=self.x.shape
	D=pairwise_distances(self.x,metric="cosine")
	aa=D[:,index]
	s=D[:,index].sum(axis=0)-D[index,index]
	return s/(r-1)    
