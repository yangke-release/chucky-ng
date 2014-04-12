#!/usr/bin/env python2

from joerntools.shelltool.PipeTool import PipeTool
from joerntools.mlutils.EmbeddingLoader import EmbeddingLoader
from joerntools.mlutils.EmbeddingSaver import EmbeddingSaver

from sklearn.metrics.pairwise import pairwise_distances

import sys

DESCRIPTION = """ Calculate the k nearest neighbors to a data point
based on an embedding. """

DEFAULT_DIRNAME = 'embedding'
DEFAULT_K = 10

class ChuckyKnnTool():
    
    def __init__(self):
        self.loader = EmbeddingLoader()
        self.saver = EmbeddingSaver()
    def _loadEmbedding(self, dirname):
        self.saver.setEmbeddingDir(dirname)
        try:
            return self.loader.load(dirname)
        except IOError:
            sys.stderr.write('Error reading embedding.\n')
            sys.exit()
    def calculateDistances(self):
        if not self.emb.dExists():
            self.emb.D = self._calculateDistanceMatrix()
            
        if not self.emb.nnExists():
            self._calculateNearestNeighbors()
            
    def _calculateNearestNeighbors(self):
        self.emb.NNV = self.emb.D.copy()
        self.emb.NNI = self.emb.D.argsort(axis=0)
        self.emb.NNV.sort(axis=0)
        
    def _calculateDistanceMatrix(self):
        return pairwise_distances(self.emb.x, metric='cosine')
    def getknn(self,node_id,dirname,k=DEFAULT_K):
        self.emb = self._loadEmbedding(dirname)
        self.calculateDistances()
        try:
            dataPointIndex = self.emb.rTOC[str(node_id)]
        except KeyError:
            sys.stderr.write('Warning: no data point found for %s\n' %
                             (node_id))
        result=[]
        for i in self.emb.NNI[0:k, dataPointIndex]:
            result.append(self.emb.TOC[i])
        return result