
# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

from pebl import data 

class TestFileParsing:
    def setUp(self):
        self.data = data.fromfile("testdata1.txt", header=True, sampleheader=True)        

    def tearDown(self):
        pass

    def test_basic_parsing(self):
        assert self.data[0][0] == 2.5, "Parsing values."
        assert self.data[0][2] == 1.7, "Parsing values."
        assert self.data[2][1] == 999.3, "Parsing values."
        assert self.data[2][2] == 12.0, "Parsing values: convert to float."

    def test_interventions(self):
        assert self.data.interventions_for_sample(0) == [0, 1], "Parsing interventions (! before/after value)."
        assert self.data.interventions_for_sample(1) == [1], "Parsing interventions (! before value)."

    def test_missingvals(self):
        assert self.data.missingvals[0][0] == False, "Parsing missingvals."
        assert self.data.missingvals[0][1] == True, "Parsing missingvals."

    def test_interventions_and_missingvals(self):
        result1 = self.data.missingvals[0][1] 
        result2 = self.data.interventions_for_sample(0)
        assert (result1 == True and result2 == [0, 1]), "Parsing both interventions and missingvals (! and X) for the same value."




def _create_data_mockup():
    a = array([[1.2, 1.4, 2.1, 2.2, 1.1],
               [2.3, 1.1, 2.1, 3.2, 1.3],
               [3.2, 0.0, 2.2, 2.5, 1.6],
               [4.2, 2.4, 3.2, 2.1, 2.8],
               [2.7, 1.5, 0.0, 1.5, 1.1],
               [1.1, 2.3, 2.1, 1.7, 3.2]
              ])

    dat = data.PeblData(a.shape, buffer=a, dtype=a.dtype)
    dat.interventions = array([[0,0,0,0,0],
                                     [0,1,0,0,0],
                                     [0,0,1,1,0],
                                     [0,0,0,0,0],
                                     [0,0,0,0,0],
                                     [0,0,0,1,0] ])
    
    dat.missingvals = array([[0,0,0,0,0],
                                   [0,0,0,0,0],
                                   [0,1,0,0,0],
                                   [0,1,0,0,0],
                                   [0,0,1,0,0],
                                   [0,0,0,0,0] ])
    
    dat._calculate_arities()
    dat.variablenames = array(["gene A", "gene B", "receptor protein C", " receptor D", "E kinase protein"])
    dat.samplenames = array(["head.wt", "limb.wt", "head.shh_knockout", "head.gli_knockout", 
                             "limb.shh_knockout", "limb.gli_knockout"])

    return dat


class TestDataObject:
    """ Test PeblData's methods and properties.

    We create a PeblData manually -- not testing file parsing here.
    
    """
    
    def setUp(self):
        self.data = _create_data_mockup()

    def tearDown(self):
        pass

    def test_numvariables(self):
        assert self.data.numvariables == 5, "Data has 5 variables."

    def test_numsamples(self):
        assert self.data.numsamples == 6, "Data has 6 samples."

    def test_subsetting_byvar(self):
        assert (self.data.subset(variables=[0,2,4]) == self.data.take([0,2,4], axis=1)).all(), "Subsetting data by variables."
        
    def test_subsetting_bysample(self):
        assert (self.data.subset(samples=[0,2]) == self.data.take([0,2], axis=0)).all(), "Subsetting data by samples."
    
    def test_subsetting_byboth(self):
        assert (self.data.subset(variables=[0,2], samples=[1,2]) == self.data[[1,2]][:,[0,2]]).all(), "Subsetting data by variable and sample."

    def test_subsetting_missingvals(self):
        subset = self.data.subset(variables=[1,2], samples=[2,3,4])
        assert (subset.missingvals == self.data.missingvals[[2,3,4]][:,[1,2]]).all(), "Missingvals in data subset."

    def test_subsetting_interventions(self):
        subset = self.data.subset(variables=[1,2], samples=[2,3,4])
        assert (subset.interventions == self.data.interventions[[2,3,4]][:,[1,2]]).all(), "Interventions in data subset."

    def test_subsetting_variablenames(self):
        subset = self.data.subset(variables=[1,2], samples=[2,3,4])
        assert subset.variablenames.tolist() == ["gene B", "receptor protein C"], "Variable names in data subset."

    def test_subsetting_samplenames(self):
        subset = self.data.subset(variables=[1,2], samples=[2,3,4])
        assert subset.samplenames.tolist() == ["head.shh_knockout", "head.gli_knockout", "limb.shh_knockout"], "Sample names in data subset."

    def test_has_missingvals(self):
        assert self.data.has_missingvals, "Check for missing values."

    def test_missingvals_indices(self):
        # [1,2,3] != [3,1,2] BUT set([1,2,3]) == set([3,1,2]) because sets have no ordering.
        missingset = set(self.data.indices_of_missingvals)
        assert missingset == set([(2,1), (3,1), (4,2)]), "Missing mask as (row,col) indices."

    def test_num_missingvals_forvariable(self):
        assert self.data.num_missingvals_for_variable(1) == 2, "Missing values for variable."

    def test_num_missingvals_forsample(self):
        assert self.data.num_missingvals_for_sample(3) == 1, "Missing values for sample."

    def test_num_missingvals_forsample2(self):
        assert self.data.num_missingvals_for_sample(0) == 0, "Missing values for sample."
        
    def test_interventions_for_sample(self):
        assert self.data.interventions_for_sample(2) == [2,3], "Interventions for sample."

    def test_noninterventions_for_sample(self):
        assert self.data.noninterventions_for_sample(2) == [0,1,4], "Non-interventions for sample."

    def test_interventions_for_variable(self):
        assert self.data.interventions_for_variable(3) ==  [2,5], "Interventions for variable."

    def test_noninterventions_for_variable(self):
        assert self.data.noninterventions_for_variable(3) == [0,1,3,4], "Non-interventions for varible."

    def test_variables_byname_simple(self):
        assert self.data.variables_byname("gene B") == 1, "Retrieving variables by name."

    def test_variables_byname_regexp(self):
        assert set(self.data.variables_byname(namelike="gene.*")) == set([0,1]), "Retrieving variables using regexp."
    
    def test_variables_byname_regexp2(self):
        assert set(self.data.variables_byname(namelike=".*protein.*")) == set([2,4]), "Retrieving variables by regexp."

    def test_samples_byname_simple(self):
        assert self.data.samples_byname("head.wt") == 0, "Retrieving samples by name."

    def test_samples_byname_regexp(self):
        assert set(self.data.samples_byname(namelike="head.*")) == set([0,2,3]), "Retrieving samples by name."

    def test_subsetting_byname(self):
        assert (self.data.subset(samples=self.data.samples_byname(namelike="head.*")) == self.data[[0,2,3]]).all(), "Subsetting data by sample names."


class TestDiscretizing:
    """Test data discretization."""

    def setUp(self):
        a = array([[1.2, 1.4, 2.1, 2.2, 1.1],
                   [2.3, 1.1, 2.1, 3.2, 1.3],
                   [3.2, 0.0, 1.2, 2.5, 1.6],
                   [4.2, 2.4, 3.2, 2.1, 2.8],
                   [2.7, 1.5, 0.0, 1.5, 1.1],
                   [1.1, 2.3, 2.1, 1.7, 3.2],
                   [2.3, 1.1, 4.3, 2.3, 1.1],
                   [3.2, 2.6, 1.9, 1.7, 1.1],
                   [2.1, 1.5, 3.0, 1.4, 1.1]
              ])

        self.data = data.PeblData(a.shape, buffer=a, dtype=a.dtype)

    def tearDown(self):
        pass

    def test_basic_discretizing(self):
        newdata = data.discretize_variables(self.data, numbins=3)
        assert newdata[:,1].tolist() == [1, 0, 0, 2, 1, 2, 0, 2, 1], "Discretizing without any parameters."

    def test_resulting_arities(self):
        newdata = data.discretize_variables(self.data, numbins=3)
        assert newdata.arities[2] == 3, "Arities of discretized data."

    def test_discretizing_with_many_equal_values(self):
        newdata = data.discretize_variables(self.data, numbins=3)
        assert newdata[:,4].tolist() == [0, 1, 2, 2, 0, 2, 0, 0, 0], "Discretizing with many equal values."

    def test_includevars(self):
        newdata = data.discretize_variables(self.data, numbins=3, includevars=[0,2])
        assert newdata[:,1].tolist() == self.data[:,1].tolist(), "Don't discretize variable if not in includevars."
        assert newdata[:,2].tolist() == [1, 1, 0, 2, 0, 1, 2, 0, 2], "Discretize variable if in includevars."

    def test_excludevars(self):
        newdata = data.discretize_variables(self.data, numbins=3, excludevars=[0,1])
        assert newdata[:,1].tolist() == self.data[:,1].tolist(), "Don't discretize variable if in excludevars."
        assert newdata[:,2].tolist() == [1, 1, 0, 2, 0, 1, 2, 0, 2], "Discretize variable if not in excludevars."
