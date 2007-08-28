import numpy
import math
import network
from copy import deepcopy
from numpy import *
from util import *
import pydot

class Posterior():
    def __init__(self, nodes, adjacency_matrices, scores):
        self.nodes = nodes
        adjacency_matrices_and_scores = sorted(zip(adjacency_matrices, scores), cmp=lambda x,y:cmp(x[1],y[1]), reverse=True)
        adjacency_matrices, scores = unzip(adjacency_matrices_and_scores)

        self.adjacency_matrices = array(adjacency_matrices)
        self.scores = array(scores)

    def _consensus_matrix(self):
        norm_scores = normalize(exp(rescale_logvalues(self.scores)))
        return sum(n*s for n,s in zip(self.adjacency_matrices, scores))

    def __iter__(self):
        for adjmat,score in zip(self.adjacency_matrices, self.scores):
            net = network.from_nodes_and_edgelist(self.nodes, adjmat)
            net.score = score
            yield net

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__getslice__(self, key.start, key.stop)
        
        net = network.from_nodes_and_edgelist(self.nodes, self.adjacency_matrices[key])
        net.score = self.scores[key]
        return net

    def __getslice__(self, i, j):
        return [self.__getitem__(x) for x in range(i,j)]

    def consensus_network(self, threshold=.3):
        features = self._consensus_matrix()
        features[features >= threshold] = 1
        features[features < threshold] = 0
        features = features.astype(bool)
        
        return network.from_nodes_and_edgelist(self.nodes, features)
 
