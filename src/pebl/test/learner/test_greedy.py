from pebl.test import testfile
from pebl import data, result
from pebl.learner import greedy

class TestGreedyLearner:
    def setUp(self):
        self.data = data.fromfile(testfile('testdata5.txt'))
        self.data.discretize()

    def test_max_iterations(self):
        g = greedy.GreedyLearner(self.data, max_iterations=100)
        g.run()
        assert g.stats.iterations == 100

    def test_max_time(self):
        g = greedy.GreedyLearner(self.data, max_time=2)
        g.run()
        runtime = g.stats.runtime

        # time based stopping criteria is approximate..
        assert runtime >= 2 and runtime < 3

    def test_max_unimproved_iterations(self):
        g1 = greedy.GreedyLearner(self.data, max_unimproved_iterations=1)
        g1.run()

        g2 = greedy.GreedyLearner(self.data, max_unimproved_iterations=100)
        g2.run()

        assert g1.stats.restarts > g2.stats.restarts



