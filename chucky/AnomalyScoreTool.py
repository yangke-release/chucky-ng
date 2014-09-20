#!/usr/bin/env python2

from joerntools.shelltool.PipeTool import PipeTool
from joerntools.mlutils.EmbeddingLoader import EmbeddingLoader
from sklearn.metrics.pairwise import pairwise_distances
from scipy.sparse import *
import numpy

import sys

DESCRIPTION = """ Calculates the center of mass of the given embedding
and returns the distance of every input line """

DEFAULT_DIRNAME = 'embedding'

class AnomalyScoreTool():
    
    def __init__(self):
        self.loader = EmbeddingLoader()

    def _loadEmbedding(self, dirname):
        try:
            return self.loader.load(dirname)
        except IOError:
            sys.stderr.write('Error reading embedding.\n')
            sys.exit()

    def analyze(self, line,dirname,triple):
	self.rFeatTable=triple[0].index2Term
	self.x=csr_matrix(csc_matrix(triple[0].matrix).T)
	print self.x.shape
	self.TOC=triple[1]
	self.rTOC=triple[2]
	#self = self._loadEmbedding(dirname)
    	try:
            dataPointIndex = self.rTOC[line]
        except KeyError:
            sys.stderr.write('Warning: no data point found for %s\n' % (line))
    	
    	return self.calculateDistance(dataPointIndex)
    	
    
    def _cosine(self,x,A,index):
	#x csr_matrix row vector 
	#A csr_matrix muti row
	m,n=A.get_shape()
	m1,n1=x.get_shape()
	#print m,n,m1,n1
	if ((n!=n1)or(m1!=1)or(m==0)or(n==0)or(m1==0)or(n1==0)):
	    return []
	#result=numpy.zeros([1,m])
	result=[]
	for i in range(0,m):
	    t=csr_matrix(A[i,:])
	    d=vstack([t,x]).tocsr()
	    tmp=pairwise_distances(d, metric='cosine')
	    #result[0,i]=tmp[0,1]
	    result.append(tmp[0,1])
	return result
    def meancos(self,index):
	r,c=self.x.shape
	s=0.0
	for i in range(0,r):
	    if i!=index:
		t=self.x[i,:]
		x=self.x[index,:]
		d=vstack([t,x]).tocsr()
		tmp=pairwise_distances(d, metric='cosine')
		s+=tmp[0,1]
	return s/(r-1)
    
    def calculateDistance(self, index): 
	self.mean=self.calculateCenterOfMass(index)
	t=csr_matrix(self.x[index,:])
	d=vstack([t,self.mean]).tocsr()
	tmp=pairwise_distances(d, metric='cosine')
	cos_with_mean=tmp[0,1];
	mean_cos=self.meancos(index)
	li=[]
	distance = (self.mean - self.x[index])
	for feat, score in zip(distance.indices, distance.data):
	    #feat_string = self.rFeatTable[feat].replace('%20', ' ')
	    feat_string=self.rFeatTable[feat]
	    li.append((float(score), feat_string))
	return (mean_cos,cos_with_mean,li)
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

