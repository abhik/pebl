"""Testing the scale of problems that pebl can handle.

How to use this
---------------
Import into python shell and call test_pebl with different sets of arguments.

"""

import numpy as N
from pebl import data, config
from pebl.learner import greedy

def test_pebl(numvars, numsamples, greedy_iters, cachesize):
    print "Testing with #vars=%d, #samples=%d, iters=%d, cachesize=%d" % (
    numvars, numsamples, greedy_iters, cachesize)

    config.set('localscore_cache.maxsize', cachesize)
    d = data.Dataset(N.random.rand(numsamples, numvars))
    d.discretize()
    g = greedy.GreedyLearner(d, max_iterations=greedy_iters)
    g.run()
    return g

if __name__ == '__main__':
    test_pebl(1000, 1000, 1000000, 1000)



