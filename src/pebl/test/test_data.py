import numpy as N

from pebl import data
from pebl.test import testfile

class TestFileParsing:
    def setUp(self):
        self.data = data.fromfile(testfile('testdata1.txt'))
        self.expected_observations = N.array([[   2.5,    0. ,    1.7],
                                              [   1.1,    1.7,    2.3],
                                              [   4.2,  999.3,   12. ]])
        self.expected_dtype = N.dtype(float)
        self.expected_varnames = ['var1', 'var2', 'var3']
        self.expected_missing = N.array([[False,  True, False],
                                         [False, False, False],
                                         [False, False, False]], dtype=bool)
        self.expected_interventions = N.array([[ True,  True, False],
                                               [False,  True, False],
                                               [False, False, False]], dtype=bool)
        self.expected_arities = [-1,-1,-1]
    def test_observations(self):
        assert (self.data.observations == self.expected_observations).all()

    def test_dtype(self):
        assert self.data.observations.dtype == self.expected_dtype

    def test_varnames(self):
        assert [v.name for v in self.data.variables] == self.expected_varnames

    def test_missing(self):
        assert (self.data.missing == self.expected_missing).all()

    def test_interventions(self):
        assert (self.data.interventions == self.expected_interventions).all()

    def test_arities(self):
        assert [v.arity for v in self.data.variables] ==  self.expected_arities

    
class TestComplexFileParsing(TestFileParsing):
    def setUp(self):
        self.data = data.fromfile(testfile('testdata2.txt'))
        self.expected_observations = N.array([[ 0.  ,  0.  ,  1.25,  0.  ],
                                              [ 1.  ,  1.  ,  1.1 ,  1.  ],
                                              [ 1.  ,  2.  ,  0.45,  1.  ]])
        self.expected_dtype = N.dtype(float) # because one continuous variable
        self.expected_varnames = ['shh', 'ptchp', 'smo', 'outcome']
        self.expected_interventions = N.array([[ True,  True, False, False],
                                               [False,  True, False, False],
                                               [False, False, False, False]], dtype=bool)
        self.expected_missing = N.array([[False, False, False, False],
                                         [False, False, False, False],
                                         [False, False, False, False]], dtype=bool)
        self.expected_arities = [2, 3, -1, 2]         

    def test_classlabels(self):
        assert self.data.variables[3].labels == ['good', 'bad']


class TestFileParsing_WithSampleNames(TestFileParsing):
    def setUp(self):
        self.data = data.fromfile(testfile('testdata3.txt'))
        self.expected_observations = N.array([[0, 0], [1, 1], [1,2]])
        self.expected_missing = N.array([[0, 0], [0, 0], [0, 0]], dtype=bool)
        self.expected_interventions = N.array([[1, 1], [0, 1], [0, 0]], dtype=bool)
        self.expected_varnames = ['shh', 'ptchp']
        self.expected_samplenames = ['sample1', 'sample2', 'sample3']
        self.expected_arities = [2,3]
        self.expected_dtype = N.dtype(int)
        
    def test_sample_names(self):
        assert [s.name for s in self.data.samples] == self.expected_samplenames

class TestFileParsing_WithSampleNames2(TestFileParsing_WithSampleNames):
    def setUp(self):
        self.data = data.fromfile(testfile('testdata4.txt')) # no tab before variable names
        self.expected_observations = N.array([[0, 0], [1, 1], [1,2]])
        self.expected_missing = N.array([[0, 0], [0, 0], [0, 0]], dtype=bool)
        self.expected_interventions = N.array([[1, 1], [0, 1], [0, 0]], dtype=bool)
        self.expected_varnames = ['shh', 'ptchp']
        self.expected_samplenames = ['sample1', 'sample2', 'sample3']
        self.expected_arities = [2,3]
        self.expected_dtype = N.dtype(int)

class TestManualDataCreations:
    def setUp(self):
        obs = N.array([[1.2, 1.4, 2.1, 2.2, 1.1],
                       [2.3, 1.1, 2.1, 3.2, 1.3],
                       [3.2, 0.0, 2.2, 2.5, 1.6],
                       [4.2, 2.4, 3.2, 2.1, 2.8],
                       [2.7, 1.5, 0.0, 1.5, 1.1],
                       [1.1, 2.3, 2.1, 1.7, 3.2] ])

        interventions = N.array([[0,0,0,0,0],
                                 [0,1,0,0,0],
                                 [0,0,1,1,0],
                                 [0,0,0,0,0],
                                 [0,0,0,0,0],
                                 [0,0,0,1,0] ])

        missing = N.array([[0,0,0,0,0],
                           [0,0,0,0,0],
                           [0,1,0,0,0],
                           [0,1,0,0,0],
                           [0,0,1,0,0],
                           [0,0,0,0,0] ])
        variablenames = ["gene A", "gene B", "receptor protein C", " receptor D", "E kinase protein"]
        samplenames = ["head.wt", "limb.wt", "head.shh_knockout", "head.gli_knockout", 
                       "limb.shh_knockout", "limb.gli_knockout"]
        self.data = data.Dataset(
                  obs, 
                  missing.astype(bool), 
                  interventions.astype(bool),
                  N.array([data.Variable(n) for n in variablenames]),
                  N.array([data.Sample(n) for n in samplenames])
        )

    def test_missing(self):
        x,y = N.where(self.data.missing)
        assert  (x == N.array([2, 3, 4])).all() and \
                (y == N.array([1, 1, 2])).all()

    def test_missing2(self):
        assert self.data.missing[N.where(self.data.missing)].tolist() == [ True,  True,  True]

    def test_missing3(self):
        assert (N.transpose(N.where(self.data.missing)) == N.array([[2, 1],[3, 1],[4, 2]])).all()

    def test_subset1(self):
        expected = N.array([[ 1.2,  2.1,  1.1],
                            [ 2.3,  2.1,  1.3],
                            [ 3.2,  2.2,  1.6],
                            [ 4.2,  3.2,  2.8],
                            [ 2.7,  0. ,  1.1],
                            [ 1.1,  2.1,  3.2]])
        assert (self.data.subset(variables=[0,2,4]).observations == expected).all()

    def test_subset2(self):
        expected = N.array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
                            [ 3.2,  0. ,  2.2,  2.5,  1.6]])
        assert (self.data.subset(samples=[0,2]).observations == expected).all()

    def test_subset3(self):
        subset = self.data.subset(variables=[0,2], samples=[1,2])
        expected = N.array([[ 2.3,  2.1],
                            [ 3.2,  2.2]])
        assert (subset.observations == expected).all()

    def test_subset3_interventions(self):
        subset = self.data.subset(variables=[0,2], samples=[1,2])
        expected = N.array([[False, False],
                            [False,  True]], dtype=bool)
        assert (subset.interventions == expected).all()

    def test_subset3_missing(self):
        subset = self.data.subset(variables=[0,2], samples=[1,2])
        expected = N.array([[False, False],
                            [False, False]], dtype=bool)
        assert (subset.missing == expected).all()
        
    def test_subset3_varnames(self):
        subset = self.data.subset(variables=[0,2], samples=[1,2])
        expected = ['gene A', 'receptor protein C']
        assert [v.name for v in subset.variables] == expected

    def test_subset3_samplenames(self):
        subset = self.data.subset(variables=[0,2], samples=[1,2])
        expected = ['limb.wt', 'head.shh_knockout']
        assert [s.name for s in subset.samples] == expected


class TestDataDiscretization:
    def setUp(self):
        self.data = data.fromfile(testfile('testdata5.txt'))
        self.data.discretize()
        self.expected_original = \
            N.array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
                     [ 2.3,  1.1,  2.1,  3.2,  1.3],
                     [ 3.2,  0. ,  1.2,  2.5,  1.6],
                     [ 4.2,  2.4,  3.2,  2.1,  2.8],
                     [ 2.7,  1.5,  0. ,  1.5,  1.1],
                     [ 1.1,  2.3,  2.1,  1.7,  3.2],
                     [ 2.3,  1.1,  4.3,  2.3,  1.1],
                     [ 3.2,  2.6,  1.9,  1.7,  1.1],
                     [ 2.1,  1.5,  3. ,  1.4,  1.1]])
        self.expected_discretized = \
            N.array([[0, 1, 1, 1, 0],
                    [1, 0, 1, 2, 1],
                    [2, 0, 0, 2, 2],
                    [2, 2, 2, 1, 2],
                    [1, 1, 0, 0, 0],
                    [0, 2, 1, 0, 2],
                    [1, 0, 2, 2, 0],
                    [2, 2, 0, 0, 0],
                    [0, 1, 2, 0, 0]])
        self.expected_arities = [3,3,3,3,3]

    def test_orig_observations(self):
        assert (self.data.original_observations == self.expected_original).all()

    def test_disc_observations(self):
        assert (self.data.observations == self.expected_discretized).all()

    def test_arity(self):
        assert [v.arity for v in self.data.variables] == self.expected_arities


class TestDataDiscretizationWithMissing:
    """Respond to Issue 32: Pebl should ignore the missing values when
    selecting bins for each data point.  Discretization for this should be
    the same as if there were no missing data, as in TestDataDiscretization.

    """
    def setUp(self):
        self.data = data.fromfile(testfile('testdata5m.txt'))
        self.data.discretize()
        self.expected_original = \
            N.array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
                     [ 2.3,  1.1,  2.1,  3.2,  1.3],
                     [ 3.2,  0. ,  1.2,  2.5,  1.6],
                     [ 4.2,  2.4,  3.2,  2.1,  2.8],
                     [ 2.7,  1.5,  0. ,  1.5,  1.1],
                     [ 1.1,  2.3,  2.1,  1.7,  3.2],
                     [ 2.3,  1.1,  4.3,  2.3,  1.1],
                     [ 3.2,  2.6,  1.9,  1.7,  1.1],
                     [ 2.1,  1.5,  3. ,  1.4,  1.1],
                     [ 0. ,  0. ,  0. ,  0. ,  0. ],
                     [ 0. ,  0. ,  0. ,  0. ,  0. ],
                     [ 0. ,  0. ,  0. ,  0. ,  0. ]])
        self.expected_discretized = \
            N.array([[0, 1, 1, 1, 0],
                    [1, 0, 1, 2, 1],
                    [2, 0, 0, 2, 2],
                    [2, 2, 2, 1, 2],
                    [1, 1, 0, 0, 0],
                    [0, 2, 1, 0, 2],
                    [1, 0, 2, 2, 0],
                    [2, 2, 0, 0, 0],
                    [0, 1, 2, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0]])
        self.expected_arities = [3,3,3,3,3]
        self.expected_missing = N.array([[False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [False, False, False, False, False],
                                         [True , True , True , True , True ],
                                         [True , True , True , True , True ],
                                         [True , True , True , True , True ]], 
                                        dtype=bool)

    def test_orig_observations(self):
        assert (self.data.original_observations == self.expected_original).all()

    def test_disc_observations(self):
        assert (self.data.observations == self.expected_discretized).all()

    def test_arity(self):
        assert [v.arity for v in self.data.variables] == self.expected_arities

    def test_missing(self):
        assert (self.data.missing == self.expected_missing).all()


class TestSelectiveDataDiscretization(TestDataDiscretization):
    def setUp(self):
        self.data = data.fromfile(testfile('testdata5.txt'))
        self.data.discretize(includevars=[0,2])
        self.expected_original = \
            N.array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
                     [ 2.3,  1.1,  2.1,  3.2,  1.3],
                     [ 3.2,  0. ,  1.2,  2.5,  1.6],
                     [ 4.2,  2.4,  3.2,  2.1,  2.8],
                     [ 2.7,  1.5,  0. ,  1.5,  1.1],
                     [ 1.1,  2.3,  2.1,  1.7,  3.2],
                     [ 2.3,  1.1,  4.3,  2.3,  1.1],
                     [ 3.2,  2.6,  1.9,  1.7,  1.1],
                     [ 2.1,  1.5,  3. ,  1.4,  1.1]])
        self.expected_discretized = \
            N.array([[ 0. ,  1.4,  1. ,  2.2,  1.1],
                     [ 1. ,  1.1,  1. ,  3.2,  1.3],
                     [ 2. ,  0. ,  0. ,  2.5,  1.6],
                     [ 2. ,  2.4,  2. ,  2.1,  2.8],
                     [ 1. ,  1.5,  0. ,  1.5,  1.1],
                     [ 0. ,  2.3,  1. ,  1.7,  3.2],
                     [ 1. ,  1.1,  2. ,  2.3,  1.1],
                     [ 2. ,  2.6,  0. ,  1.7,  1.1],
                     [ 0. ,  1.5,  2. ,  1.4,  1.1]])
        self.expected_arities = [3,-1,3,-1,-1]
        
class TestSelectiveDataDiscretization2(TestDataDiscretization):
    def setUp(self):
        self.data = data.fromfile(testfile('testdata5.txt'))
        self.data.discretize(excludevars=[0,1])
        self.expected_original = \
            N.array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
                     [ 2.3,  1.1,  2.1,  3.2,  1.3],
                     [ 3.2,  0. ,  1.2,  2.5,  1.6],
                     [ 4.2,  2.4,  3.2,  2.1,  2.8],
                     [ 2.7,  1.5,  0. ,  1.5,  1.1],
                     [ 1.1,  2.3,  2.1,  1.7,  3.2],
                     [ 2.3,  1.1,  4.3,  2.3,  1.1],
                     [ 3.2,  2.6,  1.9,  1.7,  1.1],
                     [ 2.1,  1.5,  3. ,  1.4,  1.1]])
        self.expected_discretized = \
            N.array([[ 1.2,  1.4,  1. ,  1. ,  0. ],
                    [ 2.3,  1.1,  1. ,  2. ,  1. ],
                    [ 3.2,  0. ,  0. ,  2. ,  2. ],
                    [ 4.2,  2.4,  2. ,  1. ,  2. ],
                    [ 2.7,  1.5,  0. ,  0. ,  0. ],
                    [ 1.1,  2.3,  1. ,  0. ,  2. ],
                    [ 2.3,  1.1,  2. ,  2. ,  0. ],
                    [ 3.2,  2.6,  0. ,  0. ,  0. ],
                    [ 2.1,  1.5,  2. ,  0. ,  0. ]])
        self.expected_arities = [-1,-1,3,3,3]
        
def test_arity_checking():
    try:
        # arity specified is less than number of unique values!!
        dataset = data.fromfile(testfile('testdata6.txt'))
    except data.IncorrectArityError:
        assert True
    else:
        assert False

def test_arity_checking2():
    try:
        # arity specified is MORE than number of unique values. this is ok.
        dataset = data.fromfile(testfile('testdata7.txt'))
    except:
        assert False
    
    assert [v.arity for v in dataset.variables] == [3,4,3,6]

