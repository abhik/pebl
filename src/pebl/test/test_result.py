from copy import deepcopy
from numpy import allclose
from pebl import result
from pebl import data, network
from pebl.test import testfile

class TestScoredNetwork:
    def setUp(self):
        net1 = network.Network([data.Variable(x) for x in range(5)], "0,1")
        self.sn1 = result._ScoredNetwork(net1.edges, -11.15)
        net2 = network.Network([data.Variable(x) for x in range(5)], "1,0")
        self.sn2 = result._ScoredNetwork(net2.edges, -11.15)

    def test_equality(self):
        # score is same, but different network
        assert (self.sn1 == self.sn2) == False

    def test_comparison(self):
        self.sn2.score = -10.0
        assert self.sn2 > self.sn1


def TestScoredNetworkHashing():
    # test due to a bug encountered earlier
    net = network.Network([data.Variable(x) for x in range(5)], "0,1;1,2;4,3")
    snet = result._ScoredNetwork(net.edges, -10)
    for i in xrange(1000):
        if hash(snet) != hash(deepcopy(snet)):
            assert False

class TestLearnerResult:
    size = 3
    len = 3
    zero_score = -11
    scores = [-11, -10.5, -8.5]

    def setUp(self):
        nodes = [data.Variable(x) for x in range(5)] 
        self.result = result.LearnerResult(size=self.size)
        self.result.nodes = nodes
        
        self.result.start_run()
        nets = ("0,1", "1,0" , "1,2;2,3", "4,1;1,2", "4,2;4,3")
        scores = (-10.5, -11, -8.5, -12, -13)
        for n,s in zip(nets, scores):
            self.result.add_network(network.Network(nodes, n), s)

    def test_sorting(self):
        assert self.result.networks[0].score == self.zero_score
        assert [n.score for n in self.result.networks] == self.scores

    def test_len(self):
        assert len(self.result.networks) == self.len

class TestLearnerResult2(TestLearnerResult):
    size = 0
    len = 5
    zero_score = -13
    scores = [-13, -12, -11, -10.5, -8.5]

class TestMergingResults(object):
    def setUp(self):
        nodes = [data.Variable(x) for x in range(5)] 
        nets = ("0,1", "1,0" , "1,2;2,3", "4,1;1,2", "4,2;4,3")
        scores = (-10.5, -11, -8.5, -12, -13)

        self.result1 = result.LearnerResult(size=0)
        self.result1.nodes = nodes
        self.result1.start_run()
        for n,s in zip(nets, scores):
            self.result1.add_network(network.Network(nodes, n), s)

        self.result2 = result.LearnerResult(size=0)
        self.result2.nodes = nodes
        self.result2.start_run()
        self.result2.add_network(network.Network(nodes, "1,2;2,3;3,4"), -6)
        self.result2.add_network(network.Network(nodes, "1,2;2,3;3,4;0,4;0,2"), -5.5)
        self.result2.add_network(network.Network(nodes, "0,1"), -10.5)

    def test_individual_sizes(self):
        assert len(self.result1.networks) == 5
        assert len(self.result2.networks) == 3

    def test_merged_size1(self):
        mr = result.merge(self.result1, self.result2)
        len(mr.networks) == (5+3-1) # 1 duplicate network

    def test_merged_size1(self):
        mr = result.merge([self.result1, self.result2])
        len(mr.networks) == (5+3-1) # 1 duplicate network

    def test_merged_scores(self):
        mr = result.merge([self.result1, self.result2])
        assert [n.score for n in mr.networks] == [-13, -12, -11, -10.5, -8.5, -6, -5.5]


class TestPosterior(TestMergingResults):
    def setUp(self):
        super(TestPosterior, self).setUp()
        self.merged = result.merge(self.result1, self.result2)
        self.posterior = self.merged.posterior

    def test_top_score(self):
        assert self.posterior[0].score == -5.5

    def test_top_network(self):
        assert list(self.posterior[0].edges) == [(0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]

    def test_len(self):
        assert len(self.posterior) == 7

    def test_slicing(self):
        assert self.posterior[:2][1].score == -6.0

    def test_entropy(self):
        assert allclose(self.posterior.entropy, 0.522714000397) 

    def test_consensus_net1(self):
        expected = '0,2;0,4;1,2;2,3;3,4'
        assert self.posterior.consensus_network(.5).as_string() == expected
    
    def test_consensus_net1(self):
        expected = '1,2;2,3;3,4'
        assert self.posterior.consensus_network(.8).as_string() == expected



    """


"""

if __name__ == '__main__':
    from pebl.test import run
    run()

