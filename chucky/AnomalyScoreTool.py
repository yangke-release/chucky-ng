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
        self.mean=None

    def _loadEmbedding(self, dirname):
        try:
            return self.loader.load(dirname)
        except IOError:
            sys.stderr.write('Error reading embedding.\n')
            sys.exit()

    def analyze(self, line,dirname):
	
	self.emb = self._loadEmbedding(dirname)
    	try:
            dataPointIndex = self.emb.rTOC[line]
        except KeyError:
            sys.stderr.write('Warning: no data point found for %s\n' % (line))
    	
    	return self.calculateDistance(dataPointIndex)
    	
    
    def calculateDistance(self, index):

	self.emb.D = self.calculateCenterOfMass(index)
	#print max((self.emb.D - self.emb.x[index]).data)
	distance = (self.emb.D - self.emb.x[index])
	result=[]
	for feat, score in zip(distance.indices, distance.data):
	    feat_string = self.emb.rFeatTable[feat].replace('%20', ' ')
	    result.append('{:+6.5f} {}'.format(score, feat_string))
	return result

    def calculateCenterOfMass(self, index):
        
        X = vstack([self.emb.x[:index, :], self.emb.x[index+1:, :]])
        return csr_matrix(X.mean(axis=0))

