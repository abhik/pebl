# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

from pebl import data, network, evaluator, prior, config
from pebl.test import testfile
import os
import copy


class TestBaseNetworkEvaluator:
    def setUp(self):
        self.data = data.fromfile(testfile('testdata10.txt'))
        self.neteval = evaluator.NetworkEvaluator(self.data, network.fromdata(self.data))
        self.neteval.network.edges.add_many([(1,0), (2,0), (3,0)]) # {1,2,3} --> 0

    def test_localscore(self):
        assert allclose(
            self.neteval._localscore(0, self.neteval.network.edges.parents(0)),
            -3.87120101091
        )

    def test_cache1(self):
        self.neteval._localscore(0, self.neteval.network.edges.parents(0)) 
        assert (self.neteval._localscore.hits, self.neteval._localscore.misses) == (0,1)
    
    def test_cache2(self):
        self.neteval._localscore(0, self.neteval.network.edges.parents(0)) 
        self.neteval._localscore(0, self.neteval.network.edges.parents(0)) 
        assert self.neteval._localscore.hits, self.neteval._localscore.misses == (1,1)

    def test_score1(self):
        assert allclose(self.neteval.score_network(), -15.461087517)

    def test_score2(self):
        assert (self.neteval.clear_network(), -15.6842310683)

    def test_score3(self):
        self.neteval.clear_network()
        self.neteval.alter_network(add=[(1,0),(2,0),(3,0)])
        assert allclose(self.neteval.score_network(), -15.461087517)

class TestNetworkEvalWithPrior:
    def setUp(self):
        self.data = data.fromfile(testfile('testdata10.txt'))
        self.neteval = evaluator.NetworkEvaluator(
            self.data, 
            network.fromdata(self.data), 
            prior.UniformPrior(self.data.variables.size))
        self.neteval.network.edges.add_many([(1,0),(2,0),(3,0)])

    def test_localscore(self):
        assert allclose(
            self.neteval._localscore(0, self.neteval.network.edges.parents(0)),
            -3.87120101091
        )
    
    def test_scorenetwork(self):
        assert allclose(self.neteval.score_network(), -16.961087517)

class TestSmartNetworkEvaluator:
    def setUp(self):
        self.data = data.fromfile(testfile('testdata10.txt'))
        self.ne = evaluator.SmartNetworkEvaluator(
            self.data,
            network.fromdata(self.data))
        
    def test_alter1(self):
        assert allclose(self.ne.alter_network(add=[(1,0),(2,0),(3,0)]), -15.461087517)

    def test_cache1(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        assert (self.ne._localscore.hits, self.ne._localscore.misses) == (0,4)

    def test_alter2(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        assert allclose(self.ne.alter_network(add=[(1,2)]), -15.2379439657)

    def test_cache2(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        self.ne.alter_network(add=[(1,2)])

        # NOTE: because nodes 0,1,3 didn't change, we don't even hit the cache for them!
        assert (self.ne._localscore.hits, self.ne._localscore.misses) == (0,5)
        
    def test_clear1(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        self.ne.alter_network(add=[(1,2)])
        assert allclose(self.ne.clear_network(), -15.6842310683)

    def test_score1(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        self.ne.alter_network(add=[(1,2)])
        assert allclose(
            self.ne.score_network(network.Network(self.data.variables, "1,0;2,0;3,0")),
            -15.461087517
        )

    def test_cyclic1(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        try:
            self.ne.alter_network(add=[(0,1)])
        except evaluator.CyclicNetworkError, e:
            assert True
        else:
            assert False

    def test_cyclic2(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        try:
            self.ne.alter_network(add=[(0,1)])
        except:
            pass
        
        # 0 --> 1 not added because it leads to cycle.
        assert list(self.ne.network.edges) == [(1, 0), (2, 0), (3, 0)]

    def test_alter3(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        assert allclose(self.ne.alter_network(add=[(2,3)]), -15.0556224089)
        assert allclose(
            evaluator.NetworkEvaluator(
                self.data, 
                network.Network(self.data.variables, "1,0;2,0;3,0;2,3")
            ).score_network(), 
            -15.0556224089
        )

    def test_alter4(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        self.ne.alter_network(add=[(2,3)])
        assert allclose(self.ne.alter_network(add=[(1,2)], remove=[(1,0)]), -14.8324788576)
    
    def test_alter5(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        self.ne.alter_network(add=[(2,3)])
        self.ne.alter_network(add=[(1,2)], remove=[(1,0)])
        assert allclose(self.ne.restore_network(), -15.0556224089)
        assert list(self.ne.network.edges) == [(1, 0), (2, 0), (2, 3), (3, 0)]

    def test_alter6(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        self.ne.alter_network(add=[(2,3)])
        self.ne.alter_network(add=[(1,2)], remove=[(1,0)])
        self.ne.restore_network()

        assert allclose(
            self.ne.alter_network(add=[(1,2), (1,3)], remove=[(1,0), (3,0)]),
            -14.139331677
        )
        assert list(self.ne.network.edges) == [(1, 2), (1, 3), (2, 0), (2, 3)]

    def test_alter7(self):
        self.ne.alter_network(add=[(1,0),(2,0),(3,0)])
        self.ne.alter_network(add=[(2,3)])
        self.ne.alter_network(add=[(1,2)], remove=[(1,0)])
        self.ne.restore_network()

        self.ne.alter_network(add=[(1,2), (1,3)], remove=[(1,0), (3,0)])
        assert allclose(self.ne.restore_network(), -15.0556224089)
        assert list(self.ne.network.edges) == [(1, 0), (2, 0), (2, 3), (3, 0)]

class TestMissingDataNetworkEvaluator:
    neteval_type = evaluator.MissingDataNetworkEvaluator

    def setUp(self):
        a,b,c,d,e = 0,1,2,3,4
        
        self.data = data.fromfile(testfile('testdata9.txt'))
        self.net = network.fromdata(self.data)
        self.net.edges.add_many([(a,c), (b,c), (c,d), (c,e)])
        self.neteval1 = self.neteval_type(self.data, self.net, max_iterations="10*n**2")

    def test_gibbs_scoring(self):
        # score two nets (correct one and bad one) with missing values.
        # ensure that correct one scores better. (can't check for exact score)

        # score network: {a,b}->c->{d,e}
        score1 = self.neteval1.score_network()

        # score network: {a,b}->{d,e} c
        a,b,c,d,e = 0,1,2,3,4
        net2 = network.fromdata(self.data)
        net2.edges.add_many([(a,d), (a,e), (b,d), (b,e)])
        neteval2 = self.neteval_type(self.data, net2)
        score2 = neteval2.score_network()

        # score1 should be better than score2
        print score1, score2
        assert score1 > score2, "Gibbs sampling can find goodhidden node."

    def test_gibbs_saving_state(self):
        score1 = self.neteval1.score_network()
        gibbs_state = self.neteval1.gibbs_state
        num_missing = len(self.data.missing[self.data.missing==True])

        assert len(gibbs_state.assignedvals) == num_missing, "Can save state of Gibbs sampler."

    def test_gibbs_restoring_state(self):
        score1 = self.neteval1.score_network()
        gibbs_state = self.neteval1.gibbs_state
        score2 = self.neteval1.score_network(gibbs_state=gibbs_state)
        
        # no way to check if score is correct but we can check whether everything proceeds without any errors.
        assert True


    def test_alterdata_dirtynodes(self):
        # alter data. check dirtynodes.
        self.neteval1.score_network()   # to initialize datastructures
        self.neteval1._alter_data(0, 2, 1)
        assert set(self.neteval1.data_dirtynodes) == set([2,3,4]), "Altering data dirties affected nodes."


    def test_alterdata_scoring(self):
        # score. alter data. score. alter data (back to original). score. 
        # 1st and last scores should be same.
        self.neteval1.score_network()
        score1 = self.neteval1._score_network_core()
        oldval = self.neteval1.data.observations[0][2]
        self.neteval1._alter_data(0, 2, 1)
        self.neteval1._score_network_core()
        self.neteval1._alter_data(0, 2, oldval)
        score2 = self.neteval1._score_network_core()

        assert score1 == score2, "Altering and unaltering data leaves score unchanged."

class TestMissingDataMaximumEntropyNetworkEvaluator(TestMissingDataNetworkEvaluator):
    neteval_type = evaluator.MissingDataMaximumEntropyNetworkEvaluator

"""

Test out the smart network evaluator
-------------------------------------
>>> ne3.clear_network()
-15.6842310683
>>> ne3.score_network(network.Network(data10.variables, "1,0;2,0;3,0"))
-15.461087517

>>> ne3.alter_network(add=[(0,1)])
Traceback (most recent call last):
...
CyclicNetworkError

>>> list(ne3.network.edges) # 0-->1 should not have been added
[(1, 0), (2, 0), (3, 0)]
>>> ne3.score # score should have remained the same
-15.461087517

>>> ne3.alter_network(add=[(2,3)])
-15.0556224089
>>> 
-15.0556224089

>>> ne3.alter_network(add=[(1,2)], remove=[(1,0)])
-14.8324788576
>>> ne3.restore_network()
-15.0556224089
>>> list(ne3.network.edges)
[(1, 0), (2, 0), (2, 3), (3, 0)]

>>> ne3.alter_network(add=[(1,2), (1,3)], remove=[(1,0), (3,0)])
-14.139331677
>>> list(ne3.network.edges)
[(1, 2), (1, 3), (2, 0), (2, 3)]

>>> ne3.restore_network()
-15.0556224089
>>> list(ne3.network.edges)
[(1, 0), (2, 0), (2, 3), (3, 0)]


Test the exact enumerating missing data evaluator
-------------------------------------------------

>>> data11 = data.fromfile(testfile("testdata11.txt"))
>>> exactne = evaluator.MissingDataExactNetworkEvaluator(data11, network.Network(data11.variables, "0,1;2,1;1,3"))
>>> exactne.score_network()
-14.7473210493
>>>

"""


