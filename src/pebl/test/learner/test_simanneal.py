from pebl.test import testfile
from pebl import data, result
from pebl.learner import simanneal

class TestGreedyLearner:
    def setUp(self):
        self.data = data.fromfile(testfile('testdata5.txt'))
        self.data.discretize()

    def test_default_params(self):
        s = simanneal.SimulatedAnnealingLearner(self.data)
        s.run()
        assert True

    def test_param_effect(self):
        s1 = simanneal.SimulatedAnnealingLearner(self.data)
        s1.run()
        
        s2 = simanneal.SimulatedAnnealingLearner( self.data, start_temp = 50)
        s2.run()
       
        assert s1.stats.iterations > s2.stats.iterations


