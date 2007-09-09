# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

from pebl import data
from pebl.learners import greedy, simanneal

class TestGreedyLearner:
    def test_greedy_learner_basic(self):
        dat = data.fromfile("./benchdata/benchdata.10.20.txt")
        g = greedy.GreedyLearner(dat)
        g.run()

    def test_greedy_learner_max_iterations(self):
        try:
            dat = data.fromfile("./benchdata/benchdata.10.20.txt")
            g = greedy.GreedyLearner(dat)
            g.run(greedy.stop_after_max_iterations(100))
        except:
            assert 1 == 2, "GreedyLearner with max iterations."

class TestSimulatedAnnealingLearner:
    def test_simanneal_basic(self):
        dat = data.fromfile("./benchdata/benchdata.10.20.txt")
        s = simanneal.SimulatedAnnealingLearner(dat)
        s.run()




