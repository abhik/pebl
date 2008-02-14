"""Conditional probability distributions."""

import math
from itertools import izip

import numpy as N

#
# CPD classes
#
class CPD(object):
    """Abstract base class for conditional probability distributions."""
    def __init__(self, data_): pass 
    def loglikelihood(self): pass


class MultinomialCPD(CPD):
    """Multinomial conditional probability distributions."""

    # cache shared by all instances
    lnfactorial_cache = N.array([])

    def __init__(self, data_):
        self.data = data_
        arities = [v.arity for v in data_.variables]

        # ensure that there won't be a cache miss
        maxcount = data_.samples.size + max(arities)
        if len(self.lnfactorial_cache) < maxcount:
            self._prefill_lnfactorial_cache(maxcount)
        
        # create a Conditional Probability Table (cpt)
        qi = int(N.product(arities[1:]))
        self.counts = N.zeros((qi, arities[0] + 1), dtype=int)
        
        if data_.variables.size == 1:
            self.offsets = N.array([0])
        else:
            multipliers = N.concatenate(([1], arities[1:-1]))
            offsets = N.multiply.accumulate(multipliers)
            self.offsets = N.concatenate(([0], offsets))

        # add data to cpt
        self._change_counts(data_.observations, 1)


    #
    # Public methods
    #
    def replace_data(self, oldrow, newrow):
        """Replaces a data row with a new one.
        
        Missing values are handled using some form of sampling over the
        possible values and this requires making small changes to the data.
        Instead of recreating a CPD after every change, it's far more efficient
        to simply make a small change in the CPD.

        """

        add_index = sum(i*o for i,o in izip(newrow, self.offsets))
        remove_index = sum(i*o for i,o in izip(oldrow, self.offsets))

        self.counts[add_index][newrow[0]] += 1
        self.counts[add_index][-1] += 1

        self.counts[remove_index][oldrow[0]] -= 1
        self.counts[remove_index][-1] -= 1


    def loglikelihood(self):
        """Calculates the loglikelihood of the data.

        This method implements the log of the g function (equation 12) from
        "Cooper, Herskovitz. A Bayesian Method for the Induction of
        Probabilistic Networks from Data."  
        
        """ 
        
        lnfac = self.lnfactorial_cache
        counts = self.counts

        ri = self.data.variables[0].arity
        
        result = sum( 
              lnfac[ri-1]                           # log((ri-1)!) 
            - lnfac[counts[:,-1] + ri -1]           # log((Nij + ri -1)!)
            + N.sum(lnfac[counts[:,:-1]], axis=1)   # log(Product(Nijk!))
        )

        return result

    #
    # Private methods
    #
    def _change_counts(self, observations, change=1):
        indices = N.dot(observations, self.offsets)
        child_values = observations[:,0]

        for j,k in izip(indices, child_values):
            self.counts[j,k] += change
            self.counts[j,-1] += change

    # TODO: this re-creates cache everytime it is called.
    #       can't we just append to existing cache?
    def _prefill_lnfactorial_cache(self, size):
        # logs = log(x) for x in [0, 1, 2, ..., size+10]
        #    * EXCEPT, log(0) = 0 instead of -inf.
        logs = N.concatenate(([0.0], N.log(N.arange(1, size+10, dtype=float))))

        # add.accumulate does running sums..
        MultinomialCPD.lnfactorial_cache = N.add.accumulate(logs)

