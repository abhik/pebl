"""Classes and functions for representing prior distributions and constraints."""

import numpy as N

NEGINF = float('-inf')

#
# Prior Models
#
class Prior(object):
    """Class for representing prior model.

    Priors have two aspects: 
     * soft priors: weights for each possible edge.
     * hard priors: constraints that MUST be met.

    Soft priors are specified by an energy matrix, a weight matrix taking
    values over [0,1.0].

    Hard priors are specified as:
        * edges_mustexist: a list of edge-tuples that must be rpesent
        * edges_mustnotexist: a list of edge-tuples that must not be present
        * constraints: a list of functions that take adjacency matrix as input
                       and return true if constraint met and false otherwise.

    """

    def __init__(self, num_nodes, energy_matrix=None, required_edges=[], 
                 prohibited_edges=[], constraints=[], weight=1.0):
        
        self.energy_matrix = energy_matrix
        
        # mustexist are edges that must exist. They are set as zero and the
        # rest as one. We can then perfrom a bitwise-or with the adjacency
        # matrix and if the required edges are not in the adjacency matrix, the
        # result will not be all ones.
        self.mustexist = N.ones((num_nodes, num_nodes), dtype=bool)
        for src,dest in required_edges:
            self.mustexist[src,dest] = 0

        # mustnotexist are edges that cannot be present.  They are set as one
        # and the rest as zero. We can then perform a bitwise-and with the
        # adjacency matrix and if the specified edges are present, the result
        # will not be all zeros.
        self.mustnotexist = N.zeros((num_nodes, num_nodes), dtype=bool)
        for src,dest in prohibited_edges:
            self.mustnotexist[src,dest] = 1

        self.constraints = constraints
        self.weight = weight

    # TODO: test
    @property
    def required_edges(self):
        return N.transpose(N.where(self.mustexist == 0)).tolist()

    # TODO: test
    @property
    def prohibited_edges(self):
        return N.transpose(N.where(self.mustnotexist == 1)).tolist()

    def loglikelihood(self, net):
        """Returns the log likelihood of the given network.
        
        Similar to the loglikelihood method of a Conditional Probability
        Distribution.  
        
        """

        adjmat = net.edges.adjacency_matrix

        # if any of the mustexist or mustnotexist constraints are violated,
        # return negative infinity
        if (not (adjmat | self.mustexist).all()) or \
           (adjmat & self.mustnotexist).any():
            return NEGINF

        # if any custom constraints are violated, return negative infinity
        if self.constraints and not all(c(adjmat) for c in self.constraints):
            return NEGINF

        loglike = 0.0
        if self.energy_matrix != None:
            energy = N.sum(adjmat * self.energy_matrix) 
            loglike = -self.weight * energy

        return loglike


class UniformPrior(Prior):
    """A uniform prior -- that is, every edge is equally likely."""

    def __init__(self, num_nodes, weight=1.0):
        energymat = N.ones((num_nodes, num_nodes)) * .5
        super(UniformPrior, self).__init__(num_nodes, energymat, weight=weight) 

class NullPrior(Prior):
    """A null prior which returns 0.0 for the loglikelihood.

    The name for this object is a bit confusing because the UniformPrior is
    often considered the null prior in that it doesn't favor any edge more than
    another. It still favors smaller networks and takes time to calculate the
    loglikelihood. This class provides an implementation that simply returns
    0.0 for the loglikelihood. It's a null prior in the sense that the
    resulting scores are the same as if you hadn't used a prior at all.

    """

    def __init__(self, *args, **kwargs):
        pass

    def loglikelihood(self, net):
        return 0.0

def fromconfig():
    # TODO: implement this
    return NullPrior()
