"""Class for representing posterior distribution."""

import math
from copy import deepcopy
from itertools import izip

import pydot
import numpy as N

import network
from util import *


class Posterior(object):
    """Class for representing posterior distribution.
    
    Except for trivial cases, we can only have an estimated posterior
    distribution. It is usually constructed as a list of the top N networks
    found during a search of the space of networks. 

    The pebl posterior object supports a list-like interface. So, given a
    posterior object post, one can do the following:
   
        * Access the top-scoring network: post[0]
        * Access the top 10 networks as a new posterior object: post[0:10]
        * Calculate entropy of distribution: post.entropy
        * Iterate through networks: for net in post: print net.score
     

    Note: a posterior object is immutable. That is, you cannot add and remove
    networks once it is created. See result.Result for a mutable container for
    networks.  
    
    """

    def __init__(self, nodes, adjacency_matrices, scores, sortedscores=False):
        """Creates a posterior object.

        adjacency_matrices and scores can be lists or numpy arrays.
        If sorted is True, adjacency_matrices and scores should be sorted in
        descending order of score.

        """

        if not sortedscores:
            mycmp = lambda x,y: cmp(x[1],y[1])
            adjmat_and_scores = sorted(zip(adjacency_matrices, scores), 
                                       cmp=mycmp, reverse=True)
            adjacency_matrices, scores = unzip(adjmat_and_scores)

        self.adjacency_matrices = N.array(adjacency_matrices)
        self.scores = N.array(scores)
        self.nodes = nodes


    #
    # Public interface
    #
    def consensus_network(self, threshold=.3):
        """Return a consensus network with the given threshold."""

        features = self._consensus_matrix()
        features[features >= threshold] = 1
        features[features < threshold] = 0
        features = features.astype(bool)
        
        return network.Network(self.nodes, features)

    @property
    def entropy(self):
        """The information entropy of the posterior distribution."""

        # entropy = -scores*log(scores)
        # but since scores are in log, 
        # entropy = -exp(scores)*scores
        lscores = rescale_logvalues(self.scores)
        return -N.sum(N.exp(lscores)*lscores)

    #
    # Private and special interfaces
    #
    def _consensus_matrix(self):
        norm_scores = normalize(N.exp(rescale_logvalues(self.scores)))
        return sum(n*s for n,s in zip(self.adjacency_matrices, norm_scores))

    def __iter__(self):
        """Iterate over the networks in the posterior in sorted order."""
        for adjmat,score in zip(self.adjacency_matrices, self.scores):
            net = network.Network(self.nodes, adjmat)
            net.score = score
            yield net

    def __getitem__(self, key):
        """Retrieve a specific network (and score) from the posterior."""
        if isinstance(key, slice):
            return self.__getslice__(self, key.start, key.stop)
        
        net = network.Network(self.nodes, self.adjacency_matrices[key])
        net.score = self.scores[key]
        return net

    def __getslice__(self, i, j):
        """Retrieve a subset (as a new posterior object) of the networks."""
        return Posterior(
                    self.nodes, 
                    self.adjacency_matrices[i:j], self.scores[i:j]
                )

    def __len__(self):
        """Return the number of networks in this posterior distribution."""
        return len(self.scores)


#
# Factory functions
#
def from_sorted_scored_networks(nodes, networks):
    """Create a posterior object from a list of sorted, scored networks.
    
    networks should be sorted in descending order.
    """

    return Posterior(
        nodes,
        [n.edges.adjacency_matrix for n in networks],
        [n.score for n in networks]
    )


