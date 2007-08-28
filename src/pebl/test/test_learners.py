# Want code to be py2.4 compatible. So, can't use relative imports.
import sys
sys.path.insert(0, "../")

# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

from learners import greedy, simanneal
import data


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




