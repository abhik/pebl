import numpy as N
from pebl import data, network, prior


def test_null_prior():
    net = network.Network(
        [data.DiscreteVariable(i,3) for i in xrange(5)], 
        "0,1;3,2;2,4;1,4"
    )
    p1 = prior.NullPrior()
    assert p1.loglikelihood(net) == 0.0
    net.edges.add((1,4))
    assert p1.loglikelihood(net) == 0.0

class TestUniformPrior:
    ## **Note:** The uniform prior assumes equal likelihood for each edge;
    ## thus, it penalizes networks with large number of edges.

    def setUp(self):
        self.net = network.Network(
            [data.DiscreteVariable(i,3) for i in xrange(5)], 
            "0,1;3,2;2,4;1,4"
        )
        self.p = prior.UniformPrior(len(self.net.nodes))
        self.p2 = prior.UniformPrior(len(self.net.nodes), weight=2.0)

    def test_net1(self):
        assert self.p.loglikelihood(self.net) == -2.0

    def test_net2(self):
        self.net.edges.remove((1,4))
        assert self.p.loglikelihood(self.net) == -1.5

    def test_weight1(self):
        assert self.p2.loglikelihood(self.net) == -4.0

    def test_weight2(self):
        self.net.edges.remove((1,4))
        assert self.p2.loglikelihood(self.net) == -3.0

class TestHardPriors:
    def setUp(self):
        self.net = network.Network(
            [data.DiscreteVariable(i,3) for i in xrange(5)], 
            "0,1;3,2;2,4;1,4"
        )
        self.p = prior.Prior(
            len(self.net.nodes), 
            required_edges=[(1,4),(0,1)], 
            prohibited_edges=[(3,4)], 
            constraints=[lambda am: not am[0,4]]
        )
 
    def test_net1(self):
        assert self.p.loglikelihood(self.net) == 0.0

    def test_net2(self):
        self.net.edges.remove((1,4))
        assert self.p.loglikelihood(self.net) == float('-inf')
        
    def test_net3(self):
        self.net.edges.add((3,4))
        assert self.p.loglikelihood(self.net) == float('-inf')

    def test_net4(self):
        self.net.edges.add((0,4))     
        assert self.p.loglikelihood(self.net) == float('-inf')

    def test_net5(self):
        self.net.edges.add((3,2))     
        assert self.p.loglikelihood(self.net) == 0.0
        
class TestSoftPriors:
    def setUp(self):
        self.net = network.Network(
            [data.DiscreteVariable(i,3) for i in xrange(5)], 
            "0,1;2,4;1,2"
        )
        energymat = N.array([[ 0.5,  0. ,  0.5,  0.5,  0.5],
                             [ 0.5,  0.5,  0.5,  0.5,  0. ],
                             [ 0.5,  0.5,  0.5,  0.5,  0.5],
                             [ 0.5,  0.5,  0.5,  0.5,  5. ],
                             [ 0.5,  0.5,  0.5,  0.5,  0.5]])
        self.p = prior.Prior(len(self.net.nodes), energymat)
        
    def test_net1(self):
        assert self.p.loglikelihood(self.net) == -1.0

    def test_net2(self):
        self.net.edges.remove((2,4))
        self.net.edges.add((1,4))
        assert self.p.loglikelihood(self.net) == -0.5

    def test_net3(self):
        self.net.edges.add((3,4))
        assert self.p.loglikelihood(self.net) == -6.0

class TestCombinedPriors:
    def setUp(self):
        self.net = network.Network(
            [data.DiscreteVariable(i,3) for i in xrange(5)], 
            "0,1;1,3;1,2"
        )
        energymat = N.array([[ 0.5,  0. ,  0.5,  0.5,  0.5],
                             [ 0.5,  0.5,  0.5,  0.5,  0. ],
                             [ 0.5,  0.5,  0.5,  0.5,  0.5],
                             [ 0.5,  0.5,  0.5,  0.5,  5. ],
                             [ 0.5,  0.5,  0.5,  0.5,  0.5]])
        self.p = prior.Prior(len(self.net.nodes), energymat, required_edges=[(1,2)])

    def test_net1(self):
        assert self.p.loglikelihood(self.net) == -1.0

    def test_net2(self):
        self.net.edges.remove((1,2))
        assert self.p.loglikelihood(self.net) == float('-inf')

