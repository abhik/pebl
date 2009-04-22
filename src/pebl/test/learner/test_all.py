import cPickle

from pebl.test import testfile
from pebl import data, result, config
from pebl.learner import greedy, simanneal

class TestGreedyLearner_Basic:
    learnertype = greedy.GreedyLearner

    def setUp(self):
        self.data = data.fromfile(testfile('testdata5.txt')).subset(samples=range(5))
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


## Missing data evaluators
## Added in response to issue #31 (on googlecode)
class TestGreedyWithGibbs:
    learnertype = greedy.GreedyLearner
    missing_evaluator = 'gibbs'

    def setUp(self):
        config.set('evaluator.missingdata_evaluator', self.missing_evaluator)
        self.data = data.fromfile(testfile('testdata13.txt'))
        self.learner = self.learnertype(self.data)

    def test_learner_run(self):
        self.learner.run()
        assert hasattr(self.learner, 'result')

class TestGreedyWithMaxEntGibbs(TestGreedyWithGibbs):
    missing_evaluator = 'maxentropy_gibbs'

class TestSAWithGibbs(TestGreedyWithGibbs):
    learnertype = simanneal.SimulatedAnnealingLearner
    missing_evaluator = 'gibbs'

class TestSAWithMaxEntGibbs(TestSAWithGibbs):
    missing_evaluator = 'maxentropy_gibbs'

class TestExactMethodWithHiddenData:
    def setUp(self):
        config.set('evaluator.missingdata_evaluator', 'exact')
        self.data = data.fromfile(testfile('testdata13.txt')).subset(samples=range(5))
        self.learner = greedy.GreedyLearner(self.data, max_iterations=10)

    def test_learner_run(self):
        self.learner.run()
        assert hasattr(self.learner, 'result')
