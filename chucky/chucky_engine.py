from joernInterface.JoernInterface import jutils
import os

import logging
import subprocess
import shutil
import sys

from nearestNeighbor.NearestNeighborSelector import NearestNeighborSelector
from nearestNeighbor.FunctionSelector import FunctionSelector
from GlobalAPIEmbedding import GlobalAPIEmbedding

from scipy.sparse import *
from conditionAnalyser.FunctionConditions import FunctionConditions
from conditionAnalyser.ConditionPythonEmbedder import Embedder

from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import pairwise_distances
from ReportHelper import ReportHelper
DEFAULT_REPORT_PATH='report'
def parseLocationString(string):
    x = string.split(':')
    for i in range(1,len(x)):
	x[i] = int(x[i])
    return x
class ChuckyEngine():

    def __init__(self, basedir,n_neighbors,report_path):
	self.basedir = basedir
	self.k=n_neighbors
	self.logger = logging.getLogger('chucky')
	jutils.connectToDatabase()
	self.embedder=Embedder()
	self.report_path=report_path
	
    def analyze(self, job):

        self.job=job
	cachedir=os.path.join(self.basedir, 'cache')
        self.globalAPIEmbedding = GlobalAPIEmbedding(cachedir)
	
        try:
	    #mean_syntax,mean_fun_name,mean_file_name,mean_caller
            nearestNeighbors,s0,s1,s2,s3, = self._getKNearestNeighbors()
            #for n in nearestNeighbors:
                #print str(n)+"\t"+n.location()
	    dataPointIndex=self.checkNeighborsAndGetIndex(nearestNeighbors)
	    if dataPointIndex is not None:
		termDocumentMatrix=self._calculateCheckModels(nearestNeighbors)
		if termDocumentMatrix:
		    mcc,ccm,result = self._anomaly_rating(termDocumentMatrix,dataPointIndex)
		    self._outputResult(nearestNeighbors,s0,s1,s2,s3,mcc,ccm,result)
		else:
		    self.logger.warning("Could not find any conditions in all neighbors! Job skiped!\n")
        except subprocess.CalledProcessError as e:
            self.logger.error(e)
        else:
	    pass

    """
    Determine the k nearest neighbors for the
    current job.
    """
    def _getKNearestNeighbors(self):
	considerCaller=False
	if len(self.job.sourcesinks.parameter_set)>0:
	    considerCaller=True
	self.knn = NearestNeighborSelector(self.basedir,considerCaller)
        self.knn.setK(self.k)
	
	'''
	FIXME:Make additional check for the correctness of job and jobset.For example what if the jobset is None or empty Set.
	'''
	if self.job.job_set:
	    #batch operation using specified sources/sinks
	    jobset=self.job.getJobSet()
	    symbolUsers=[]
	    for job in jobset:
		symbolUsers.append(job.function)
	else:
	    #just analyse one function and use single sources/sinks in it iteratively
	    entitySelector = FunctionSelector()
	    symbolUsers = entitySelector.selectFunctionsUsingSymbol(self.job.getSourceSinks().getSingleSource())
	    
	if len(symbolUsers) <  self.k+1:
	    self.logger.warning('Job skipped, '+str(len(symbolUsers)-1)+' neighbors found, but '+str( self.k)+' required.\n')
	    return [],[],[],[],[]
	
        return self.knn.getNearestNeighbors(self.job.function, symbolUsers)
	
    def _calculateCheckModels(self, symbolUsers):
       
	li=[]
	flag=False
	for i, symbolUser in enumerate(symbolUsers):
	    feats=self._getAllSourceFeats(symbolUser,self.job.sourcesinks)
	    pair=(i,feats)
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
    
    def _outputResult(self,nearestNeighbors,data0,data1,data2,data3,mcc,ccm, result):
	m0=sum(data0)/(self.k)#semantic
	m1=sum(data1)/(self.k)#func_name
	m2=sum(data2)/(self.k)#file_name
	m3=sum(data3)/(self.k)#caller
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
	if(self.report_path is not None):
	    helper=ReportHelper(self.job.function,nearestNeighbors,self.report_path)
	    helper.setSourceSinks(self.job.sourcesinks)
	    helper.setScore(score)
	    helper.setFeature(feat)
	    helper.setSpecificity(spec)
	    helper.setMeanConditionCos(mcc)
	    helper.setConditionCosWithMean(ccm)
	    helper.setSemanticSimilarities(data0)
	    helper.setFuncNameSimilarities(data1)
	    helper.setFileNameSimilarities(data2)
	    helper.setCallerSetSimilarities(data3)
	    helper.generate()
	    
        print '{:< 6.5f}\t{:30}\t{:10}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(score, self.job.function, self.job.function.node_id,str(self.job.sourcesinks),feat,m0,m1,m2,m3,mcc,ccm,spec,self.job.function.location(),len(nearestNeighbors)-1)	
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
	    self.logger.warning('Job skipped, no enough qualified neighbors found.\n')
	    return None
	#ids=[n.node_id for n in nearestNeighbors]
	for i,n in enumerate(nearestNeighbors):
	    if str(self.job.function.node_id)==str(n.node_id):
		return i
	self.logger.warning('Warning: no data point found for %s.\n' % (str(self.job.function.node_id)))
	return None
	    
    def meancos(self,index):
	r,c=self.x.shape
	D=pairwise_distances(self.x,metric="cosine")
	aa=D[:,index]
	s=D[:,index].sum(axis=0)-D[index,index]
	return s/(r-1)
