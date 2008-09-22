"""Testing the scale of problems that pebl can handle."""

import numpy as N
from pebl import data, config
from pebl.learner import greedy

def test_pebl(numvars=100, numsamples=100, greedy_iters=1000000):
    config.set('localscore_cache.maxsize', 1000000)
    d = data.Dataset(N.random.rand(numsamples, numvars))
    d.discretize()
    g = greedy.GreedyLearner(d, max_iterations=greedy_iters)
    g.run()

if __name__ == '__main__':
    print "Testing with numvars=100, numsamples=100, iterations=1M"
    test_pebl()

    print "Testing with numvars=1000, numsamples=1000, iterations=1M"
    test_pebl()


