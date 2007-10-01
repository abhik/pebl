# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

from pebl import data
from pebl.learners import greedy, simanneal
import os

TESTDATA = """2	0	0	2	0	0	2	1	2	0
2	1	2	0	2	0	2	1	0	0
0	2	1	0	0	1	0	1	0	0
2	0	1	2	2	0	0	0	2	2
0	2	0	1	0	1	0	1	0	0
0	1	2	0	0	1	0	1	2	0
2	1	0	2	0	1	0	0	2	1
0	0	1	0	0	0	0	2	1	2
0	0	2	0	2	0	0	0	0	0
1	0	2	0	0	1	2	0	0	2
1	1	0	2	0	0	0	1	2	2
2	1	1	1	2	1	0	2	1	0
0	2	1	0	0	1	2	1	0	2
1	1	1	2	2	1	0	1	2	0
1	0	0	2	0	0	1	1	0	0
1	1	2	1	2	0	0	1	2	1
1	1	0	2	0	1	1	1	1	1
2	1	0	2	1	0	0	0	0	0
0	2	0	1	0	1	2	1	0	2
1	0	1	1	1	2	0	1	0	2
"""

class TestLearners:
    def setUp(self):
        f = open("test3.txt", 'w')
        f.write(TESTDATA)
        f.close()

    def tearDown(self):
        os.remove("test3.txt")

    def test_greedy_learner_basic(self):
        dat = data.fromfile("test3.txt")
        g = greedy.GreedyLearner(dat)
        g.run()

    def test_greedy_learner_max_iterations(self):
        dat = data.fromfile("test3.txt")
        g = greedy.GreedyLearner(dat)
        g.run(greedy.stop_after_max_iterations(100))

    def test_simanneal_basic(self):
        dat = data.fromfile("test3.txt")
        s = simanneal.SimulatedAnnealingLearner(dat)
        s.run()

    def test_learner_result_posterior(self):
        dat = data.fromfile("test3.txt")
        g = greedy.GreedyLearner(dat)
        g.run(greedy.stop_after_max_iterations(100))
        g.result.posterior.consensus_network(.4)
        
