"""Classes and functions for working with datasets."""

from __future__ import with_statement
import re
import copy
from itertools import groupby

import numpy as N

from pebl.util import *
from pebl import discretizer
from pebl import config

#
# Module parameters
#
_pfilename = config.StringParameter(
    'data.filename',
    'File to read data from.',
    config.fileexists(),
)

_ptext = config.StringParameter(
    'data.text',
    'The text of a dataset included in config file.',
    default=''
)

_pdiscretize = config.IntParameter(
    'data.discretize',
    'Number of bins used to discretize data. Specify 0 to indicate that '+\
    'data should not be discretized.',
    default=0
)

#
# Exceptions
#
class ParsingError(Exception): 
    """Error encountered while parsing an ill-formed datafile."""
    pass

class IncorrectArityError(Exception):
    """Error encountered when the datafile speifies an incorrect variable arity.

    If variable arity is specified, it should be greater than the number of
    unique observation values for the variable.

    """
    
    def __init__(self, errors):
        self.errors = errors

    def __repr__(self):
        msg = "Incorrect arity specified for some variables.\n"
        for v,uniquevals in errors:
            msg += "Variable %s has arity of %d but %d unique values.\n" % \
                   (v.name, v.arity, uniquevals)

class ClassVariableError(Exception):
    """Error with a class variable."""
    msg = """Data for class variables must include only the labels specified in
    the variable annotation."""


#
# Variables and Samples
#
class Annotation(object):
    """Additional information about a sample or variable."""

    def __init__(self, name, *args):
        # *args is for subclasses
        self.name = str(name)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__,  self.name)

class Sample(Annotation):
    """Additional information about a sample."""
    pass 

class Variable(Annotation): 
    """Additional information about a variable."""
    arity = -1

class ContinuousVariable(Variable): 
    """A variable from a continuous domain."""
    def __init__(self, name, param):
        self.name = str(name)

class DiscreteVariable(Variable):
    """A variable from a discrete domain."""
    def __init__(self, name, param):
        self.name = str(name)
        self.arity = int(param)

class ClassVariable(DiscreteVariable):
    """A labeled, discrete variable."""
    def __init__(self, name, param):
        self.name = str(name)
        self.labels = [l.strip() for l in param.split(',')]
        self.label2int = dict((l,i) for i,l in enumerate(self.labels))
        self.arity = len(self.labels)

#
# Main class for dataset
#
class Dataset(object):
    def __init__(self, observations, missing=None, interventions=None, 
                 variables=None, samples=None, skip_stats=False):
        """Create a pebl Dataset instance.

        A Dataset consists of the following data structures which are all
        numpy.ndarray instances:

        * observations: a 2D matrix of observed values. 
            - dimension 1 is over samples, dimension 2 is over variables.
            - observations[i,j] is the observed value for jth variable in the ith
              sample.

        * missing: a 2D binary mask for missing values
            - missing[i,j] = 1 IFF observation[i,j] is missing
        
        * interventions: a 2D binary mask for interventions
            - interventions[i,j] = 1 IFF the jth variable was intervened upon in
              the ith sample.
        
        * variables,samples: 1D array of variable or sample annotations
        
        This class provides a few public methods to manipulate datasets; one can
        also use numpy functions/methods directly.

        Required/Default values:

             * The only required argument is observations (a 2D numpy array).
             * If missing or interventions are not specified, they are assumed to
               be all zeros (no missing values and no interventions).
             * If variables or samples are not specified, appropriate Variable or
               Sample annotations are created with only the name attribute.

        """

        self.observations = observations
        self.missing = missing
        self.interventions = interventions
        self.variables = variables
        self.samples = samples

        # With a numpy array X, we can't do 'if not X' to check the
        # truth value because it raises an exception. So, we must use the
        # non-pythonic 'if X is None'
        
        obs = observations
        if missing is None:
            self.missing = N.zeros(obs.shape, dtype=bool)
        if interventions is None:
            self.interventions = N.zeros(obs.shape, dtype=bool)
        if variables is None:
            self.variables = N.array([Variable(str(i)) for i in xrange(obs.shape[1])])
            self._guess_arities()
        if samples is None:
            self.samples = N.array([Sample(str(i)) for i in xrange(obs.shape[0])])

        if not skip_stats:
            self._calc_stats()

    # 
    # public methods
    # 
    def subset(self, variables=None, samples=None):
        """Returns a subset of the dataset (and metadata).
        
        Specify the variables and samples for creating a subset of the data.
        variables and samples should be a list of ids. If not specified, it is
        assumed to be all variables or samples. 

        Some examples:
        
            - d.subset([3], [4])
            - d.subset([3,1,2])
            - d.subset(samples=[5,2,7,1])
        
        Note: order matters! d.subset([3,1,2]) != d.subset([1,2,3])

        """

        variables = variables if variables is not None else range(self.variables.size)
        samples = samples if samples is not None else range(self.samples.size)

        return Dataset(
            self.observations[N.ix_(samples,variables)],
            self.missing[N.ix_(samples,variables)],
            self.interventions[N.ix_(samples,variables)],
            self.variables[variables],
            self.samples[samples],
            skip_stats = True
        )

    def _subset_ni_fast(self, variables):
        ds = _FastDataset.__new__(_FastDataset)

        if not self.has_interventions:
            ds.observations = self.observations[:,variables]
            ds.samples = self.samples
        else:
            samples = N.where(self.interventions[:,variables[0]] == False)[0] 
            ds.observations = self.observations[samples][:,variables]
            ds.samples = self.samples[samples]

        ds.variables = self.variables[variables]
        return ds


    # TODO: test
    def subset_byname(self, variables=None, samples=None):
        """Returns a subset of the dataset (and metadata).

        Same as Dataset.subset() except that variables and samples can be
        specified by their names.  
        
        Some examples:

            - d.subset(variables=['shh', 'genex'])
            - s.subset(samples=["control%d" % i for i in xrange(10)])

        """

        vardict = dict((v.name, i) for i,v in enumerate(self.variables))
        sampledict = dict((s.name, i) for i,s in enumerate(self.samples))
        
        # if name not found, we let the KeyError be raised
        variables = [vardict[v] for v in variables] if variables else variables
        samples = [sampledict[s] for s in samples] if samples else samples

        return self.subset(variables, samples)



    def discretize(self, includevars=None, excludevars=[], numbins=3):
        """Discretize (or bin) the data in-place.

        This method is just an alias for pebl.discretizer.maximum_entropy_discretizer()
        See the module documentation for pebl.discretizer for more information.

        """
        self.original_observations = self.observations.copy()
        self = discretizer.maximum_entropy_discretize(
           self, 
           includevars, excludevars, 
           numbins
        ) 


    def tofile(self, filename, *args, **kwargs):
        """Write the data and metadata to file in a tab-delimited format."""
        
        with file(filename, 'w') as f:
            f.write(self.tostring(*args, **kwargs))


    def tostring(self, linesep='\n', variable_header=True, sample_header=True):
        """Return the data and metadata as a string in a tab-delimited format.
        
        If variable_header is True, include variable names and type.
        If sample_header is True, include sample names.
        Both are True by default.

        """

        def dataitem(row, col):
            val = "X" if self.missing[row,col] else str(self.observations[row,col])
            val += "!" if self.interventions[row,col] else ''
            return val
        
        def variable(v):
            name = v.name

            if isinstance(v, ClassVariable):
                return "%s,class(%s)" % (name, ','.join(v.labels))    
            elif isinstance(v, DiscreteVariable):
                return "%s,discrete(%d)" % (name, v.arity)
            elif isinstance(v, ContinuousVariable):
                return "%s,continuous" % name
            else:
                return v.name

        # ---------------------------------------------------------------------

        # python strings are immutable, so string concatenation is expensive!
        # preferred way is to make list of lines, then use one join.
        lines = []

        # add variable annotations
        if sample_header:
            lines.append("\t".join([variable(v) for v in self.variables]))
        
        # format data
        nrows,ncols = self.shape
        d = [[dataitem(r,c) for c in xrange(ncols)] for r in xrange(nrows)]
        
        # add sample names if we have them
        if sample_header and hasattr(self.samples[0], 'name'):
            d = [[s.name] + row for row,s in zip(d,self.samples)]

        # add data to lines
        lines.extend(["\t".join(row) for row in d])
        
        return linesep.join(lines)


    #
    # public propoerties
    #
    @property
    def shape(self):
        """The shape of the dataset as (number of samples, number of variables)."""
        return self.observations.shape


    #
    # private methods/properties
    #
    def _calc_stats(self):
        self.has_interventions = self.interventions.any()
        self.has_missing = self.missing.any()
    
    def _guess_arities(self):
        """Guesses variable arity by counting the number of unique observations."""

        for col,var in enumerate(self.variables):
            var.arity = N.unique(self.observations[:,col]).size
            var.__class__ = DiscreteVariable


    def check_arities(self):
        """Checks whether the specified airty >= number of unique observations.

        The check is only performed for discrete variables.

        If this check fails, the CPT and other data structures would fail.
        So, we should raise error while loading the data. Fail Early and Explicitly!

        """
        
        errors = [] 
        for col,v in enumerate(self.variables):
            if isinstance(v, DiscreteVariable):
                uniquevals = N.unique(self.observations[:,col]).size
                if v.arity < uniquevals:
                    errors.append((v, uniquevals))

        if errors:
            raise IncorrectArityError(errors)


class _FastDataset(Dataset):
    """A version of the Dataset class created by the _subset_ni_fast method.

    The Dataset._subset_ni_fast method creates a quick and dirty subset that
    skips many steps. It's a private method used by the evaluator module. Do
    not use this unless you know what you're doing.  
    
    """
    pass


#
# Factory Functions
#
def fromfile(filename):
    """Parse file and return a Dataset instance.

    The data file is expected to conform to the following format

        - comment lines begin with '#' and are ignored.
        - The first non-comment line *must* specify variable annotations
          separated by tab characters.
        - data lines specify the data values separated by tab characters.
        - data lines *can* include sample names
    
    A data value specifies the observed numeric value, whether it's missing and
    whether it represents an intervention:

        - An 'x' or 'X' indicate that the value is missing
        - A '!' before or after the numeric value indicates an intervention

    Variable annotations specify the name of the variable and, *optionally*,
    the data type.

    Examples include:

        - Foo                     : just variable name
        - Foo,continuous          : Foo is a continuous variable
        - Foo,discrete(3)         : Foo is a discrete variable with arity of 3
        - Foo,class(normal,cancer): Foo is a class variable with arity of 2 and
                                    values of either normal or cancer.

    """
    
    with file(filename) as f:
        return fromstring(f.read())


def fromstring(stringrep, fieldsep='\t'):
    """Parse the string representation of a dataset and return a Dataset instance.
    
    See the documentation for fromfile() for information about file format.
    
    """

    # parse a data item (examples: '5' '2.5', 'X', 'X!', '5!')
    def dataitem(item, v):
        item = item.strip()

        intervention = False
        missing = False
        
        # intervention?
        if item[0] == "!":
            intervention = True
            item = item[1:]
        elif item[-1] == "!":
            intervention = True
            item = item[:-1]

        # missing value?
        if item[0] in ('x', 'X') or item[-1] in ('x', 'X'):
            missing = True
            item = "0" if not isinstance(v, ClassVariable) else v.labels[0]

        # convert to expected data type
        val = item
        if isinstance(v, ClassVariable):
            try:
                val = v.label2int[val]
            except KeyError:
                raise ClassVariableError()

        elif isinstance(v, DiscreteVariable):
            try:
                val = int(val)
            except ValueError:
                msg = "Invalid value for discrete variable %s: %s" % (v.name, val)
                raise ParsingError(msg)

        elif isinstance(v, ContinuousVariable):
            try:
                val = float(val)
            except ValueError:
                msg = "Invalid value for continuous variable %s: %s" % (v.name, val)
                raise ParsingError(msg)
        else:
            # if not specified, try parsing as float or int
            if '.' in val:
                try:
                    val = float(val)
                except:
                    msg = "Cannot convert value %s to a float." % val
                    raise ParsingError(msg)
            else:
                try:
                    val = int(val)
                except:
                    msg = "Cannot convert value %s to an int." % val
                    raise ParsingError(msg)

        return (val, missing, intervention)


    dtype_re = re.compile("([\w\d_-]+)[\(]*([\w\d\s,]*)[\)]*") 
    def variable(v):
        # MS Excel encloses cells with punctuations in double quotes 
        # and many people use Excel to prepare data
        v = v.strip("\"")

        parts = v.split(",", 1)
        if len(parts) is 2:  # datatype specified?
            name,dtype = parts
            match = dtype_re.match(dtype)
            if not match:
                raise ParsingError("Error parsing variable header: %s" % v)
            dtype_name,dtype_param = match.groups()
            dtype_name = dtype_name.lower()
        else:
            name = parts[0]
            dtype_name, dtype_param = None,None

        vartypes = {
            None: Variable,
            'continuous': ContinuousVariable,
            'discrete': DiscreteVariable,
            'class': ClassVariable
        }
        
        return vartypes[dtype_name](name, dtype_param)

    # -------------------------------------------------------------------------

    # split on all known line seperators, ignoring blank and comment lines
    lines = (l.strip() for l in stringrep.splitlines() if l)
    lines = (l for l in lines if not l.startswith('#'))
    
    # parse variable annotations (first non-comment line)
    variables = lines.next().split(fieldsep)
    variables = N.array([variable(v) for v in variables])

    # split data into cells
    d = [[c for c in row.split(fieldsep)] for row in lines]

    # does file contain sample names?
    samplenames = True if len(d[0]) == len(variables) + 1 else False
    samples = None
    if samplenames:
        samples = N.array([Sample(row[0]) for row in d])
        d = [row[1:] for row in d]
    
    # parse data lines and separate into 3 numpy arrays
    #    d is a 3D array where the inner dimension is over 
    #    (values, missing, interventions) transpose(2,0,1) makes the inner
    #    dimension the outer one
    d = N.array([[dataitem(c,v) for c,v in zip(row,variables)] for row in d]) 
    obs, missing, interventions = d.transpose(2,0,1)

    # pack observations into bytes if possible (they're integers and < 255)
    dtype = 'int' if obs.dtype.kind is 'i' else obs.dtype
    
    # x.astype() returns a casted *copy* of x
    # returning copies of observations, missing and interventions ensures that
    # they're contiguous in memory (should speedup future calculations)
    d = Dataset(
        obs.astype(dtype),
        missing.astype(bool),
        interventions.astype(bool), 
        variables, 
        samples,
    )
    d.check_arities()
    return d


def fromconfig():
    """Create a Dataset from the configuration information.

    Loads data and discretizes (if requested) based on configuration
    parameters.
    
    """

    fname = config.get('data.filename')
    text = config.get('data.text')
    if text:
        data_ = fromstring(text)
    else:
        if not fname:
            raise Exception("Filename (nor text) for dataset not specified.")
        data_ = fromfile(fname)

    numbins = config.get('data.discretize')
    if numbins > 0:
        data_.discretize(numbins=numbins)
    
    return data_


def merge(datasets, axis=None):
    """Merges multiple datasets.

    datasets should be a list of Dataset objects.
    axis should be either 'variables' or 'samples' and determines how the
    datasets are merged.  
    
    """

    if axis == 'variables':
        variables = N.hstack(tuple(d.variables for d in datasets))
        samples = datasets[0].samples
        stacker = N.hstack
    else:
        samples = N.hstack(tuple(d.samples for d in datasets))
        variables = datasets[0].variables
        stacker = N.vstack

    missing = stacker(tuple(d.missing for d in datasets))
    interventions = stacker(tuple(d.interventions for d in datasets))
    observations = stacker(tuple(d.observations for d in datasets))

    return Dataset(observations, missing, interventions, variables, samples)


