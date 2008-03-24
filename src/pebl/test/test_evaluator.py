"""
======================
Testing pebl.evaluator
======================


>>> from pebl import data, network, evaluator, prior
>>> from pebl.test import testfile
>>> data10 = data.fromfile(testfile('testdata10.txt'))


Test out the base network evaluator
-----------------------------------

>>> neteval1 = evaluator.NetworkEvaluator(data10, network.fromdata(data10))
>>> neteval1.network.edges.add_many([(1,0), (2,0), (3,0)]) # {1,2,3} --> 0
>>> neteval1._cpd(0, neteval1.network.edges.parents(0)).__class__
<class 'pebl.cpd.MultinomialCPD'>
>>> neteval1._cpd(1, neteval1.network.edges.parents(1)).__class__
<class 'pebl.cpd.MultinomialCPD'>

>>> neteval1._localscore(0, neteval1.network.edges.parents(0))
-3.8712010109078907
>>> neteval1._localscore.hits, neteval1._localscore.misses
(0, 1)
>>> neteval1._localscore(0, neteval1.network.edges.parents(0))
-3.8712010109078907
>>> neteval1._localscore.hits, neteval1._localscore.misses
(1, 1)
>>> neteval1.score_network()
-15.461087517014249
>>> neteval1.clear_network()
-15.68423106832846
>>> neteval1.alter_network(add=[(1,0),(2,0),(3,0)])
-15.461087517014249


Specifying a prior
------------------
>>> neteval2 = evaluator.NetworkEvaluator(data10, network.fromdata(data10), prior.UniformPrior(data10.variables.size))
>>> neteval2.network.edges.add_many([(1,0),(2,0),(3,0)])

>>> neteval2._localscore(0, neteval2.network.edges.parents(0))
-3.8712010109078907
>>> neteval2.score_network()
-16.961087517014249
>>> neteval1.score_network()
-15.461087517014249

Test out the smart network evaluator
-------------------------------------

>>> ne3 = evaluator.SmartNetworkEvaluator(data10, network.fromdata(data10))
>>> ne3.alter_network(add=[(1,0),(2,0),(3,0)])
-15.461087517014249
>>> ne3._localscore.hits, ne3._localscore.misses
(0, 4)
>>> ne3.alter_network(add=[(1,2)])
-15.237943965700039
>>> ne3._localscore.hits, ne3._localscore.misses 
(0, 5)

**Note:** because nodes 0,1,3 did not change, we don't even hit the cache for them.

>>> ne3.clear_network()
-15.68423106832846
>>> ne3.score_network(network.Network(data10.variables, "1,0;2,0;3,0"))
-15.461087517014249

>>> ne3.alter_network(add=[(0,1)])
Traceback (most recent call last):
...
CyclicNetworkError

>>> list(ne3.network.edges) # 0-->1 should not have been added
[(1, 0), (2, 0), (3, 0)]
>>> ne3.score # score should have remained the same
-15.461087517014249

>>> ne3.alter_network(add=[(2,3)])
-15.055622408906084
>>> evaluator.NetworkEvaluator(data10, network.Network(data10.variables, "1,0;2,0;3,0;2,3")).score_network()
-15.055622408906084

>>> ne3.alter_network(add=[(1,2)], remove=[(1,0)])
-14.832478857591873
>>> ne3.restore_network()
-15.055622408906084
>>> list(ne3.network.edges)
[(1, 0), (2, 0), (2, 3), (3, 0)]

>>> ne3.alter_network(add=[(1,2), (1,3)], remove=[(1,0), (3,0)])
-14.13933167703193
>>> list(ne3.network.edges)
[(1, 2), (1, 3), (2, 0), (2, 3)]
>>> ne3.restore_network()
-15.055622408906084
>>> list(ne3.network.edges)
[(1, 0), (2, 0), (2, 3), (3, 0)]


Test the exact enumerating missing data evaluator
-------------------------------------------------

>>> data11 = data.fromfile(testfile("testdata11.txt"))
>>> exactne = evaluator.MissingDataExactNetworkEvaluator(data11, network.Network(data11.variables, "0,1;2,1;1,3"))
>>> exactne.score_network()
-14.747321049251569
>>>

"""

# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

from pebl import data, network, evaluator
from pebl.test import testfile
import os
import copy


class TestMissingDataNetworkEvaluator:
    neteval_type = evaluator.MissingDataNetworkEvaluator

    def setUp(self):
        a,b,c,d,e = 0,1,2,3,4
        
        self.data = data.fromfile(testfile('testdata9.txt'))
        self.net = network.fromdata(self.data)
        self.net.edges.add_many([(a,c), (b,c), (c,d), (c,e)])
        self.neteval1 = self.neteval_type(self.data, self.net)

    def test_gibbs_scoring(self):
        # score two nets (correct one and bad one) with missing values.
        # ensure that correct one scores better. (can't check for exact score)
        stopping_criteria = lambda iters,n: iters >= 10*n**2

        # score network: {a,b}->c->{d,e}
        score1 = self.neteval1.score_network(stopping_criteria=stopping_criteria)

        # score network: {a,b}->{d,e} c
        a,b,c,d,e = 0,1,2,3,4
        net2 = network.fromdata(self.data)
        net2.edges.add_many([(a,d), (a,e), (b,d), (b,e)])
        neteval2 = self.neteval_type(self.data, net2)
        score2 = neteval2.score_network(stopping_criteria=stopping_criteria)

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
        score2 = self.neteval1.score_network(gibbs_state=gibbs_state, stopping_criteria=lambda i,n: i>0)
        
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


