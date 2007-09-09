# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

from pebl import distributions, network, data

def _create_data_and_net():
    a = array([
                [0, 0, 1, 1, 0],
                [0, 1, 0, 0, 1],
                [1, 1, 0, 2, 2],
                [1, 0, 1, 2, 1],
                [0, 2, 2, 1, 2],
                [0, 1, 2, 0, 2],
                [1, 1, 2, 0, 2],
                [1, 1, 2, 0, 2],
                [1, 1, 2, 1, 2],
                [1, 2, 2, 1, 0]
    # arities:   2  3  3  3  3
    ])
    dat = data.PeblData(a.shape, buffer=a, dtype=a.dtype)
    dat._calculate_arities()
    net = network.fromdata(dat)
    return dat, net 


class TestConditionalProbabilityTable:
    def setUp(self):
        self.data, self.net = _create_data_and_net()
        # CPT for {node 1-4} --> {node 0}
        self.cpt1 = distributions.ConditionalProbabilityTable(self.data)

    def test_CPT_counts_shape(self):
        # counts.shape == (qi, ri + 1) where 
        #   qi=number of parent configurations and ri=child.arity
        assert self.cpt1.counts.shape == (81, 3), "CPT datastructure should be of correct size."

    def test_CPT_offsets(self):
        assert self.cpt1.offsets.tolist() == [0, 1, 3, 9, 27], "CPT list offset mask"

    def test_CPT_counts(self):
        # [{0,1}, 1, 2, 0, 2] maps to index 61.
        # [0, 1, 2, 0, 2] occurs once.
        # [1, 1, 2, 0, 2] occurs twice.
        assert self.cpt1.counts[61].tolist() == [1,2,3], "Contents of CPT."

    def test_CPT_counts_zero(self):
        # counts array should be zero-initialized.
        assert self.cpt1.counts[0].tolist() == [0,0,0], "Contents of CPT."

    def test_CPT_addcounts(self):
        self.cpt1.add_count([0,1,2,0,2])
        assert self.cpt1.counts[61].tolist() == [2,2,4], "Adding Counts to CPT."

    def test_CPT_removecounts(self):
        self.cpt1.remove_count([1,1,2,0,2])
        assert self.cpt1.counts[61].tolist() == [1,1,2], "Removing counts from CPT."

    def test_CPT2_counts(self):
        # CPT for {} -> {node 0} (no parents)
        # make sure we can create a CPT with null parent set
        cpt2 = distributions.ConditionalProbabilityTable(self.data.subset(variables=[0]))
        assert cpt2.counts[0].tolist() == [4, 6, 10], "Contents of CPT with null parent set."


class TestMultinomialDistribution:
    def setUp(self):
        self.data, self.net = _create_data_and_net()
        self.dist = distributions.MultinomialDistribution(self.data)

    def test_lnfactorial_cache_exists(self):
       assert self.dist.lnfactorial_cache is not None and len(self.dist.lnfactorial_cache), "lnfactorial cache exists."

    def test_lnfactorial_cache(self):
        cache = self.dist.lnfactorial_cache
        assert cache[0] == 0.0 and \
               cache[5] - 4.7874917427820458 <= .0001 and \
               cache[8] - 10.604602902745251 <= .0001, "Checking correcteness of lnfactorial cache"
    
    def test_loglikelihood(self):
        """Test the correctness of the log likelihood calculation on a very small dataset."""
        
        #
        # Below is the derived calculation for the loglikelihood of the parentset for node 0.
        # Calculation done according to the g function from Cooper and Herskovits.
        #
        # data: 0110   parentset: {1,2,3} --> {0}
        #       1001
        #       1110
        #       1110
        #       0011
        #
        # ri = child.arity = 2
        #
        # parent config - (Nij+ri-1)!   -   Pi[Nijk!]
        # -------------------------------------------
        # 000             (0+2-1)!           0!0!
        # 001             (1+2-1)!           0!1!
        # 010             (0+2-1)!           0!0!
        # 011             (1+2-1)!           1!0!
        # 100             (0+2-1)!           0!0!
        # 101             (0+2-1)!           0!0!
        # 110             (3+2-1)!           1!2!
        # 111             (0+2-1)!           0!0!
        #
        # likelihood  = Pi[[(ri-1)!/(Nij+ri-1)!] Pi[Nijk])
        #             = 1!0!0!/1! x 1!0!1!/2! x 1!0!0!/1! x
        #             = 1!1!0!/2! x 1!1!2!/4! x 1!0!0!/1!
        #
        #             = 1         x 1/2       x 1 x
        #             = 1/2       x 1/12      x 1
        #             = 1/48
        # loglikelihood = ln(1/48) = -3.87120101107
        a = array([[0, 1, 1, 0],
                   [1, 0, 0, 1],
                   [1, 1, 1, 0],
                   [1, 1, 1, 0],
                   [0, 0, 1, 1]
            ])
        data2 = data.PeblData(a.shape, buffer=a, dtype=a.dtype)
        data2._calculate_arities()
        net2 = network.fromdata(data2)
        sf2 = distributions.MultinomialDistribution(data2)

        assert sf2.loglikelihood() - -3.87120101107 <= .0001, "Checking for correct loglikelihood." 
    
    def test_loglikelihood_null_parentset(self):
        a = array([[0, 1, 1, 0],
                   [1, 0, 0, 1],
                   [1, 1, 1, 0],
                   [1, 1, 1, 0],
                   [0, 0, 1, 1]
            ])
        data2 = data.PeblData(a.shape, buffer=a, dtype=a.dtype)
        data2._calculate_arities()
        net2 = network.fromdata(data2)
        sf2 = distributions.MultinomialDistribution(data2.subset(variables=[0]))

        assert sf2.loglikelihood() - -4.09434456222 <= .001, "Checking for correct loglikelihood with null parentset."
         

