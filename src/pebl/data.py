"""A Class for representing datasets and functions to create and manipulate them."""

import re
from numpy import ndarray, array, unique, nonzero, zeros, searchsorted
from util import *

class PeblData(ndarray):
    """A numpy.ndarray subclass for storing data and metadata.

    Data is accessed as a 2D matrix with samples in rows (dimension 1) and variables in columns (dimension 2).
    PeblData instances can also maintain the following metadata:

        - sample names
        - variable names
        - variable arities
        - missing values
        - the intervened variable(s) for each sample

    Although a PeblData instance can be used anywhere a numpy array can, not all operations on them are completely
    intuitive.  Data slicing using numpy methods will work but the metadata in the resulting subset will be invalid.
    If you wish to use the metadata in a data subset, use the L{subset} method instead.

    For PeblData method arguments and return values, samples and variables are represented by their index.
    Use L{samples_byname} and L{variables_byname} to retrieve indices given name or regular expression.

    """
    
    # The list of data structures added to ndarray by pebl.
    # If you modify this list, modify__new__ and  subset() to handle these.
    _pebl_metadata = ['interventions', 'missingvals', 'arities', 'samplenames', 'variablenames']
    
    # PeblData takes precendence over other array types
    __array_priority__ = 10

    def __new__(cls, *args, **kwargs):
        """This method should never be called directly."""

        # no_metadata means do not waste time initializing metadata (because it
        # will be re-initialized or copied from another PeblData instance).. 
        no_metadata = kwargs.pop("no_metadata", False)
        pd =  ndarray.__new__(cls, *args, **kwargs)

        if not no_metadata:
            pd.interventions = zeros(pd.shape, dtype=bool)
            pd.missingvals = zeros(pd.shape, dtype=bool)
            pd.arities = zeros(pd.shape[1], dtype=int)
            pd.samplenames = zeros(pd.shape[0], dtype="S1")
            pd.variablenames = zeros(pd.shape[1], dtype="S1")

        return pd

    def __array_wrap__(self, array):
        pd = PeblData(shape=array.shape, buffer=array, dtype=array.dtype, no_metadata=True)
        self._copy_pebl_metadata_to(pd)
        return pd
    
    def _copy_pebl_metadata_to(self, pd):
        """Copy metadata from self to PeblData instance."""

        for attr in PeblData._pebl_metadata:
            if hasattr(self, attr):
                setattr(pd, attr, getattr(self, attr))

    def _copy_pebl_metadata_from(self, pd):
        """Copy metadata from PeblData instance to self."""

        for attr in PeblData._pebl_metadata:
            if hasattr(pd, attr):
                setattr(self, attr, getattr(pd, attr))
    

    def _calculate_arities(self):
        """Calculate the arity (domain,rank) of variables in the dataset."""

        self.arities = array([len(unique(self[:,varnum]).flatten()) for varnum in range(self.numvariables)])

    def _list_indices(self, list_, names, namelike=""):
        """Search a list using exact names or regular expressions."""
        
        # list_ can be a numpy array so 'not list_' is not same as 'list_ == None'
        if list_ == None or len(list_) == 0:
            return []

        # let's work with regular lists instead of ndarray
        list_ = list_.tolist()
        
        # if namelike was provided, names is ignored..
        if namelike:
            # use regular expression to find matching indices
            regexp = re.compile(namelike)
            indices = [i for i,name in enumerate(list_) if regexp.search(name)]
            return indices

        namelist = ensure_list(names)
        try:
            indices = [list_.index(name) for name in namelist]
        except:
            raise ValueError("Name not in list.")
        
        return cond(isinstance(names, list), indices, indices[0])

    def subset(self, variables=[], samples=[], ignore_all_metadata=False, ignore_names=False):
        """Return a subset of the dataset.
        
        @param variables: list of variable indices.
        @param samples: list of sample indices.

        If quick is False, subset contains a subset of metadata also. 
        If quick is True, subset's metadata will be invalid and should not be used. 

        Sample usage:
            - pd.subset(variables=1)
            - pd.subset(variables=[1,4,5], samples=[0,2])
            - pd.subset(variables=pd.variables_byname("gene x"))
            - pd.subset(samples=pd.samples_byname("mouse somite.*"))

        """

        if not variables: 
            variables = range(self.numvariables)
        if not samples: 
            samples = range(self.numsamples)

        sub = self[samples][:,variables]
        
        if not ignore_all_metadata:
            sub.missingvals = self.missingvals[samples][:,variables]
            sub.interventions = self.interventions[samples][:,variables]
            sub.arities = self.arities[variables]
            
            if not ignore_names:
                sub.variablenames = self.variablenames[variables]
                sub.samplenames = self.samplenames[samples]

        return sub
    
    def variables_byname(self, names=[], namelike=""):
        """Return list of variables (as variable indices) matching exact name or regular expression.

        @param names: list of variable names to match.
        @param namelike: regular expression to use for matching variable names.

        """

        return self._list_indices(self.variablenames, names, namelike)
    
    def samples_byname(self, names=[], namelike=""):
        """Return list of samples (as sample indices) matching exact name or regular expression.

        @param names: list of sample names to match.
        @param namelike: regular expression to use for matching sample names.

        """

        return self._list_indices(self.samplenames, names, namelike)

    def num_missingvals_for_variable(self, var):
        """Return the number of missing values for given variable."""

        mv = self.missingvals[:,var]
        return len(mv[mv == True])

    def num_missingvals_for_sample(self, sample):
        """Return the number of missing values for given sample."""

        mv = self.missingvals[sample]
        return len(mv[mv == True])

    def latent_variables(self):
        """Return the list of latent variables."""

        return [v for v in range(self.numvariables) 
                    if self.num_missingvals_for_variable(v) is self.numsamples
               ]

    def interventions_for_sample(self, sample):
        """Return list of variables intervened upon in the given sample."""

        return [i for i,intervention in enumerate(self.interventions[sample]) if intervention]
   
    def noninterventions_for_sample(self, sample):
        """Return list of variables *not* intervened upon in the given sample."""

        return [i for i,intervention in enumerate(self.interventions[sample]) if not intervention]

    def interventions_for_variable(self, variable):
        """Return list of samples in which the given variable was intervened upon."""

        return [i for i,intervention in enumerate(self.interventions[:,variable]) if intervention]

    def noninterventions_for_variable(self, variable):
        """Return list of samples in whcih the gien variable was *not* intervened upon."""
        return [i for i,intervention in enumerate(self.interventions[:,variable]) if not intervention]
    
    def tofile(self, filename):
        """Write the data and metadata to file in a tab-delimited format."""
        stringrep = self.tostring()

        f = open(filename, 'w')
        f.write(stringrep)
        f.close()
    
    def tostring(self, linesep='\n'):
        """Return the data and metadata as a String."""

        def getcell(row, col):
            missing = self.missingvals[row][col]
            intervention = self.interventions[row][col]
            val = cond(missing, "X", str(self[row][col]))
            val += cond(intervention, "!", "")
            return val
        
        lines = []
        
        if self.variablenames and len(self.variablenames) > 0 and len(self.variablenames[0]) > 0:
            # variablenames exists, is a non-empty list and the first element is not just ""
            lines.append("\t".join(self.variablenames))
            
        for rownum in xrange(self.numsamples):
            line = [getcell(rownum, colnum) for colnum in xrange(self.numvariables)]
            lines.append("\t".join(line))
        
        return linesep.join(lines)

    @property 
    def indices_of_missingvals(self):
        """The indices (as (sample,variable)) for missing values."""

        rows, cols = nonzero(self.missingvals)
        return [(row,col) for row,col in zip(rows,cols)]
   
    @property
    def has_missingvals(self):
        """Boolean property specifying whether the dataset has any missing values."""

        return self.missingvals.any()

    @property
    def numsamples(self):
        """The number of samples in the dataset."""

        return self.shape[0]
        
    @property
    def numvariables(self):
        """The number of variables in the dataset."""

        return self.shape[1]


## This implementation calculates bin edges by trying to make bins equal sized.. 
## 
## input:  [3,7,4,4,4,5]
## output: [0,1,0,0,0,1]
##
## Note: All 4s discretize to 0.. which makes bin sizes unequal..                                                 
def discretize_variables(pd, includevars=None, excludevars=[], numbins=3):

    attrs = Struct()
    pd._copy_pebl_metadata_to(attrs)
    pd2 = pd.copy()
    
    includevars = ensure_list(includevars or range(pd.numvariables))
    binsize = pd.numsamples//numbins

    for var in includevars:
        if var not in excludevars:
            row = pd2[:,var]
            argsorted = row.argsort()
            binedges = [row[argsorted[binsize*b - 1]] for b in range(numbins)][1:]
            pd2[:,var] = searchsorted(binedges, row)

    # if discreitizing all variables, set array datatype to byte
    if len(includevars) == pd2.numvariables and not excludevars:
        pd2 = pd2.astype('byte')

    pd2._copy_pebl_metadata_from(attrs)
    pd2._calculate_arities()
    return pd2


def discretize_variables_in_groups(pd, samplegroups, includevars=None, excludevars=[], numbins=3):
    attrs = Struct()
    pd._copy_pebl_metadata_to(attrs)
    pd2 = pd.copy()
    includevars = ensure_list(includevars or range(pd.numvariables))
    
    for samplegroup in samplegroups:
        pd2[samplegroup] = discretize_variables(pd[samplegroup], includevars, excludevars, numbins)

    # if discreitizing all variables, set array datatype to byte
    if len(includevars) == pd.numvariables and not excludevars:
        pd2 = pd2.astype('byte')

    pd2._copy_pebl_metadata_from(attrs)
    pd2._calculate_arities()
    return pd2


def fromfile(filename, header=False, sampleheader=False):
    f = open(filename)
    data_obj = fromstring(f.read(), header, sampleheader)
    f.close()
    return data_obj


def fromstring(stringrep, header=False, sampleheader=False):
    fieldsep = "\t"

    # function to process each data item in file
    def process_item(item):
        item = item.strip()

        intervention = False
        missing = False

        if item[0] == "!":
            intervention = True
            item = item[1:]
        elif item[-1] == "!":
            intervention = True
            item = item[:-1]

        if item[0] in ('x', 'X') or item[-1] in ('x', 'X'):
            missing = True
            item = "0"

        # first try converting to int, then to float
        try:
            value = int(item)
        except ValueError:
            try:
                value = float(item)
            except:
                print "Error parsing value: '%s'" % item
                raise ValueError

        return (value, intervention, missing)


    def process_row(row):
        items = row.split(fieldsep)
        samplename = ''
        if sampleheader:
            samplename = items[0]
            items = items[1:]
        
        row = [process_item(item) for item in items]
        values, interventions, missingvals = unzip(row)

        return (values, interventions, missingvals, samplename)


    # ------------------------------------------------------
   
    # split on all known line seperators.
    rows = re.split("\r\n|\r|\n", stringrep)
    rows = [row for row in rows if row] # remove blank lines
    
    # is the first line a header line with column names?
    varnames = None
    if header:
        varnames = rows.pop(0).split(fieldsep)
        if sampleheader:
            # first column of all rows is name of sample, so remove it..
            varnames = varnames[1:]
   
    data, interventions, missingvals, samplenames = unzip([process_row(row) for row in rows])

    # convert data to numpy array
    da = array(data)
    pd = PeblData(shape=da.shape, buffer=da, dtype=da.dtype, no_metadata=True)

    # convert to array of bytes (if possible).
    # this will be possible for discrete data (which should be a common case)
    if pd.dtype.kind is 'i' and pd.max() < 255:
         pd = pd.astype('byte')
   
    # set PeblData metadata
    pd.variablenames = cond(header, 
                            array(varnames), 
                            array(["Var %s" % i for i in xrange(pd.numvariables)]))
    pd.samplenames = cond(sampleheader, 
                          array(samplenames), 
                          array(["Sample %s" % i for i in xrange(pd.numsamples)]))
    pd.interventions = array(interventions).astype(bool)
    pd.missingvals = array(missingvals).astype(bool)

    # calculate arities
    pd._calculate_arities()
    return pd


