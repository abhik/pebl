import cPickle

from pebl.test import testfile
from pebl import data, result
from pebl.learner import greedy, simanneal

class TestGreedyLearner_Basic:
    learnertype = greedy.GreedyLearner

    def setUp(self):
        self.data = data.fromfile(testfile('testdata5.txt'))
        self.data.discretize()
        self.learner = self.learnertype(self.data)

    def test_result(self):
        self.learner.run()
        assert hasattr(self.learner, 'result')

    def test_pickleable(self):
        try:
            x = cPickle.dumps(self.learner)
            self.learner.run()
            y = cPickle.dumps(self.learner)
            assert 1 == 1
        except:
            assert 1 == 2

class TestSimAnnealLearner_Basic(TestGreedyLearner_Basic):
    learnertype = simanneal.SimulatedAnnealingLearner

