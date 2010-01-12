""" Collection of data discretization algorithms."""

import numpy as N
from util import as_list
import data

def maximum_entropy_discretize(indata, includevars=None, excludevars=[], numbins=3):
    """Performs a maximum-entropy discretization of data in-place.
    
    Requirements for this implementation:

        1. Try to make all bins equal sized (maximize the entropy)
        2. If datum x==y in the original dataset, then disc(x)==disc(y) 
           For example, all datapoints with value 3.245 discretize to 1
           even if it violates requirement 1.
        3. Number of bins reflects only the non-missing data.
     
     Example:

         input:  [3,7,4,4,4,5]
         output: [0,1,0,0,0,1]
        
         Note that all 4s discretize to 0, which makes bin sizes unequal. 

     Example: 

         input:  [1,2,3,4,2,1,2,3,1,x,x,x]
         output: [0,1,2,2,1,0,1,2,0,0,0,0]

         Note that the missing data ('x') gets put in the bin with 0.0.

    """

    # includevars can be an atom or list
    includevars = as_list(includevars) 
   
    # determine the variables to discretize
    includevars = includevars or range(indata.variables.size)
    includevars = [v for v in includevars if v not in excludevars]
   
    for v in includevars:
        # "_nm" means "no missing"
        vdata = indata.observations[:,v]
        vmiss = indata.missing[:,v]
        vdata_nm = vdata[-vmiss]
        argsorted = vdata_nm.argsort()
        # Find bin edges (cutpoints) using no-missing 
        binsize = len(vdata_nm)//numbins
        binedges = [vdata_nm[argsorted[binsize*b - 1]] for b in range(numbins)][1:]
        # Discretize full data. Missings get added to bin with 0.0.
        indata.observations[:,v] = N.searchsorted(binedges, vdata)

        oldvar = indata.variables[v]
        newvar = data.DiscreteVariable(oldvar.name, numbins)
        newvar.__dict__.update(oldvar.__dict__) # copy any other data attached to variable
        newvar.arity = numbins
        indata.variables[v] = newvar

    # if discretized all variables, then cast observations to int
    if len(includevars) == indata.variables.size:
        indata.observations = indata.observations.astype(int)
    
    return indata


