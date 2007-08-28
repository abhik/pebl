import math
from util import ensure_list
from numpy import *

class Distribution(object):
    def __init__(self, pebldata): pass 
    def loglikelihood(self): pass

#############################################################################################################
class ConditionalProbabilityTable(object):
    def __init__(self, pebldata):
        qi = int(product(pebldata.arities[1:]))
        self.counts = zeros((qi, pebldata.arities[0] + 1), dtype=int)

        if pebldata.numvariables is 1:
            self.offsets = [0]
        else:
            multipliers = concatenate(([1], pebldata.arities[1:-1]))
            offsets = multiply.accumulate(multipliers)
            self.offsets = concatenate(([0], offsets))

        self.add_counts(pebldata)

    def _change_counts(self, pebldata, change=1):
        indices = dot(pebldata, self.offsets)
        child_values = pebldata[:,0]

        for j,k in zip(indices, child_values):
            self.counts[j][k] += change
            self.counts[j][-1] += change

    def add_counts(self, pebldata):
        return self._change_counts(pebldata, 1)

    def add_count(self, datum):
        self._change_counts(array([datum]), 1)          
    
    def remove_count(self, datum):
        self._change_counts(array([datum]), -1)

class MultinomialDistribution(Distribution):
    __title__ = "Multinomial Distribution"
    lnfactorial_cache = array([])

    def __init__(self, pebldata):
        max_count = pebldata.numsamples + max(pebldata.arities)
        if len(self.lnfactorial_cache) < max_count:
            self.prefill_lnfactorial_cache(max_count)
        
        self.arities = pebldata.arities
        self.cpt = ConditionalProbabilityTable(pebldata)

    def add_data(self, datarow):
        self.cpt.add_count(datarow)

    def remove_data(self, datarow):
        self.cpt.remove_count(datarow)

    def loglikelihood(self):
        lnfac = self.lnfactorial_cache
        counts = self.cpt.counts

        ri = self.arities[0]
        qi = int(product(self.arities[1:]))
        
        result = sum( 
              lnfac[ri-1] 
            - lnfac[counts[:,-1] + ri -1] 
            + sum(lnfac[counts[:,:-1]], axis=1) 
        )

        return result


    def prefill_lnfactorial_cache(self, size):
        # logs = log(x) for x in [0, 1, 2, ..., size+10]
        #    * EXCEPT, log(0) = 0 instead of -inf.
        logs = concatenate(([0.0], log(arange(1, size+10, dtype=float))))

        # add.accumulate does running sums..
        MultinomialDistribution.lnfactorial_cache = add.accumulate(logs)

