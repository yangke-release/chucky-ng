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
    
    def __init__(self,rFeatTable,matrix,TOC,rTOC):
	self.rFeatTable=rFeatTable
	self.x=matrix
	self.TOC=TOC
	self.rTOC=rTOC
	
    def analyze(self, funcIdStr):
    	try:
            dataPointIndex = self.rTOC[funcIdStr]
        except KeyError:
            sys.stderr.write('Warning: no data point found for %s\n' % (funcIdStr))
    	
    	return self.calculateDistance(dataPointIndex)
    
    def calculateDistance(self, index): 
	self.mean=self.calculateCenterOfMass(index)
	distance = (self.mean - self.x[index])
	result=[]
	for feat, score in zip(distance.indices, distance.data):
	    #feat_string = self.rFeatTable[feat].replace('%20', ' ')
	    feat_string = self.rFeatTable[feat]
	    result.append((float(score), feat_string))
	return result
    
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

