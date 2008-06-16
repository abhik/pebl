from numpy import array, allclose
from pebl import data, cpd
from pebl.test import testfile

def test_cextension():
    try:
        from pebl import _cpd
    except:
        assert False

class TestCPD_Py:
    """
    Deriving loglikelihood manually
    -------------------------------

    Below is the derived calculation for the loglikelihood of the parentset for
    node 0.  Calculation done according to the g function from Cooper and
    Herskovits. This test is done with binary varaibles because doing more on paper
    is tedious. There are other tests that check for correct loglikelihood with
    more complicated data.

    data: 0110   parentset: {1,2,3} --> {0}
          1001
          1110
          1110
          0011

    ri = child.arity = 2

    parent config - (Nij+ri-1)!   -   Pi[Nijk!]
    -------------------------------------------
    000             (0+2-1)!           0!0!
    001             (1+2-1)!           0!1!
    010             (0+2-1)!           0!0!
    011             (1+2-1)!           1!0!
    100             (0+2-1)!           0!0!
    101             (0+2-1)!           0!0!
    110             (3+2-1)!           1!2!
    111             (0+2-1)!           0!0!

    likelihood  = Pi[[(ri-1)!/(Nij+ri-1)!] Pi[Nijk])
                = 1!0!0!/1! x 1!0!1!/2! x 1!0!0!/1! x
                  1!1!0!/2! x 1!1!2!/4! x 1!0!0!/1!

                = 1         x 1/2       x 1 x
                  1/2       x 1/12      x 1

                = 1/48

    loglikelihood = ln(1/48) = -3.87120101107
    """

    cpdtype = cpd.MultinomialCPD_Py

    def setUp(self):
        self.data = data.Dataset(array([[0, 1, 1, 0],
                                        [1, 0, 0, 1],
                                        [1, 1, 1, 0],
                                        [1, 1, 1, 0],
                                        [0, 0, 1, 1]]))
        for v in self.data.variables: 
            v.arity = 2
        self.cpd = self.cpdtype(self.data)
    
    def test_lnfactorial_cache(self):
        expected = array([  0.        ,   0.        ,   0.69314718,   1.79175947,
                            3.17805383,   4.78749174,   6.57925121,   8.52516136,
                            10.6046029,  12.80182748,  15.10441257,  17.50230785,
                            19.9872145,  22.55216385,  25.19122118,  27.89927138,
                            30.67186011])
        assert allclose(self.cpd.lnfactorial_cache, expected)

    def test_offsets(self):
        assert (self.cpd.offsets == array([0,1,2,4])).all()

    def test_counts(self):
        expected = array([[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0],
                          [1, 2, 3],
                          [0, 1, 1],
                          [0, 0, 0],
                          [1, 0, 1],
                          [0, 0, 0]])
        assert (self.cpd.counts == expected).all()

    def loglikelihood(self):
        assert allclose(self.cpd.loglikelihood(), -3.87120101091)

    def test_replace1_loglikelihood(self):
        # Do a noop replace.
        self.cpd.replace_data(array([0,1,1,0]), array([0,1,1,0]))
        assert allclose(self.cpd.loglikelihood(), -3.87120101091)

    def test_replace1_counts(self):
        self.cpd.replace_data(array([0,1,1,0]), array([0,1,1,0]))
        expected = array([[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0],
                          [1, 2, 3],
                          [0, 1, 1],
                          [0, 0, 0],
                          [1, 0, 1],
                          [0, 0, 0]])
        assert (self.cpd.counts == expected).all()
    
    def test_replace2_loglikelihood(self):
        self.cpd.replace_data(self.data.observations[0], array([1,1,1,0]))
        assert allclose(self.cpd.loglikelihood(), -2.77258872224)

    def test_replace2_counts(self):
        self.cpd.replace_data(self.data.observations[0], array([1,1,1,0]))
        expected = array([[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0],
                          [0, 3, 3],
                          [0, 1, 1],
                          [0, 0, 0],
                          [1, 0, 1],
                          [0, 0, 0]])
        assert (self.cpd.counts == expected).all()

    def test_undo_loglikelihood(self):
        self.cpd.replace_data(self.data.observations[0], array([1,1,1,0]))
        self.cpd.replace_data(array([1,1,1,0]),array([0,1,1,0]))
        assert allclose(self.cpd.loglikelihood(), -3.87120101091)
    
    def test_undo_counts(self):
        self.cpd.replace_data(self.data.observations[0], array([1,1,1,0]))
        self.cpd.replace_data(array([1,1,1,0]),array([0,1,1,0]))
        expected = array([[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0],
                          [1, 2, 3],
                          [0, 1, 1],
                          [0, 0, 0],
                          [1, 0, 1],
                          [0, 0, 0]])
        assert (self.cpd.counts == expected).all()
    
    def test_replace_with_ndarray(self):
        self.cpd.replace_data(array([0,1,1,0]), array([1,1,1,0]))
        assert allclose(self.cpd.loglikelihood(), -2.77258872224)


class TestCPD_C(TestCPD_Py):
    cpdtype = cpd.MultinomialCPD_C

    # The C version doesn't expose all datastructures to python
    def test_lnfactorial_cache(self): pass
    def test_offsets(self): pass
    def test_counts(self): pass
    def test_replace1_counts(self): pass
    def test_replace2_counts(self): pass
    def test_undo_counts(self): pass

class TestCPD2_Py:
    """
    Can we properly handle nodes with no parents?
    ----------------------------------------------

    With data=[1,0,1,1,0] for a node with no parents:

        ri = child.arity = 2

        parent config   (Nij+ri-1)!       Pi[Nijk!]
        -------------------------------------------
        null set        (5+2-1)!          3!2!

        likelihood = Pi[[(ri-1)!/(Nij+ri-1)!] Pi[Nijk])
                   = 1!3!2!/6!
                   = 12/720 = 1/60

        loglikelihood = ln(1/60) 
                      = -4.09434456
    """
    cpdtype = cpd.MultinomialCPD_Py

    def setUp(self):
        self.data = data.Dataset(array([[1],
                                        [0],
                                        [1],
                                        [1],
                                        [0]]))
        self.data.variables[0].arity = 2
        self.cpd = self.cpdtype(self.data)     

    def test_offsets(self):
        assert (self.cpd.offsets == array([0])).all()

    def test_counts(self):
        assert (self.cpd.counts == array([[2,3,5]])).all()

    def test_loglikelihood(self):
        assert allclose(self.cpd.loglikelihood(), -4.09434456)

class TestCPD2_C(TestCPD2_Py):
    cpdtype = cpd.MultinomialCPD_C

    # The C version doesn't expose all datastructures to python

    def test_offsets(self): pass
    def test_counts(self): pass


class TestMultinomialCPD_C:
    def setUp(self):
        self.data = data.fromfile(testfile("greedytest1-200.txt"))

    def test_cpt_reuse(self):
        # check that we don't have SegFault or BusError
        
        # instead of freeing memory, _cpd will reuse it
        for i in xrange(10000):
            c = cpd.MultinomialCPD_C(self.data)
            c.loglikelihood()
            del c

    def test_cpt_ceate_delete(self):
        # "del c" will reuse memory while "del c2" will free it
        for i in xrange(10000):
            c = cpd.MultinomialCPD_C(self.data)
            c2 = cpd.MultinomialCPD_C(self.data)
            c.loglikelihood()
            c2.loglikelihood()
            del c
            del c2


