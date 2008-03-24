"""Miscellaneous utility functions."""

import numpy as N
import math
import os.path
from copy import copy

def as_list(c):
    """Ensures that the result is a list.

    If input is a list/tuple/set, return it.
    If it's None, return empty list.
    Else, return a list with input as the only element.
    
    """

    if isinstance(c, (list,tuple,set)):
        return c
    elif c is None:
        return []
    else:
        return [c]
 
def cond(condition, expr1, expr2):
    """Marked for deletion.. Python2.5 provides this."""
    
    if condition:
        return expr1
    else:
        return expr2


def flatten(seq):
    """Given a nested datastructure, flatten it."""

    lst = []
    for el in seq:
        if type(el) in [list, tuple, set]:
            lst.extend(flatten(el))
        else:
            lst.append(el)
    return lst


def normalize(lst):
    """Normalizes a list of numbers (sets sum to 1.0)."""

    if not isinstance(lst, N.ndarray):
        lst = N.array(lst)

    return lst/lst.sum()

def rescale_logvalues(lst):
    """Rescales a list of log values by setting max value to 0.0

    This function is necessary when working with list of log values. Without
    it, we could have overflows. This is a lot faster than using arbitrary
    precision math libraries.
    
    """

    if not isinstance(lst, N.ndarray):
        lst = N.array(lst) 
    
    return lst - lst.max()

def rescaleAndExponentiateLogValues(lst):
    lst = N.array(lst)
    lst = lst - lst.max()
    lst = N.exp(lst)

    return lst


_LogZero = 1.0e-100
_MinLogExp = math.log(_LogZero);
def logadd(x, y):
    """Adds two log values.
    
    Ensures accuracy even when the difference between values is large.
    
    """
    if x < y:
        temp = x
        x = y
        y = temp

    z = math.exp(y - x)
    logProb = x + math.log(1.0 + z)
    if logProb < _MinLogExp:
        return _MinLogExp
    else:
        return logProb

def logsum(lst):
    """Sums a list of log values, ensuring accuracy."""
    
    if not isinstance(lst, N.ndarray):
        lst = N.array(lst)
    
    maxval = lst.max()
    lst = lst - maxval
    return reduce(logadd, lst) + maxval


## from webpy (webpy.org)
def autoassign(self, locals):
    """
    Automatically assigns local variables to `self`.
    Generally used in `__init__` methods, as in:

        def __init__(self, foo, bar, baz=1): autoassign(self, locals())
    """
    for (key, value) in locals.iteritems():
        if key == 'self': 
            continue
        setattr(self, key, value)


def unzip(l, *jj):
    """Opposite of zip().

    *jj is a tuple of list indexes (or keys) to extract or unzip. If not
    specified, all items are unzipped.

    """
	
    if jj==():
	    jj=range(len(l[0]))
    rl = [[li[j] for li in l] for j in jj] # a list of lists
    if len(rl)==1:
        rl=rl[0] #convert list of 1 list to a list
    return rl


def nestediter(lst1, lst2):
    """A syntactic shortform for doing nested loops."""
    for i in lst1:
        for j in lst2:
            yield (i,j)



def cartesian_product(list_of_lists):
    """Given n lists (or sets), generate all n-tuple combinations.

    >>> list(cartesian_product([[0,1], [0,1,"foo"]]))
    [(0, 0), (0, 1), (0, 'foo'), (1, 0), (1, 1), (1, 'foo')]

     >>> list(cartesian_product([[0,1], [0,1], [0,1]]))
     [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
    
    """

    head,rest = list_of_lists[0], list_of_lists[1:]
    if len(rest) is 0:
        for val in head:
            yield (val,)
    else:
        for val in head:
            for val2 in cartesian_product(rest):
                yield (val,) + val2


def probwheel(items, weights):
    """Randomly select an item from a weighted list of items."""
    
    # convert to numpy array and normalize
    weights = normalize(N.array(weights))

    # edges for bins
    binedges = weights.cumsum()
    randval = N.random.random()
    for item, edge in zip(items, binedges):
        if randval <= edge:
            return item
    
    # should never reach here.. but might due to rounding errors.
    return items[-1]


def logscale_probwheel(items, logweights):
    """Randomly select an item from a [log] weighted list of items.
    
    Fucntion just rescale logweights and exponentiates before calling
    probwheel. 
    
    """
    return probwheel(items, N.exp(rescale_logvalues(logweights)))


def entropy_of_list(lst):
    """Given a list of values, generate histogram and calculate the entropy."""

    unique_values = N.unique(lst)
    unique_counts = N.array([float(len([i for i in lst if i == unique_val])) for unique_val in unique_values])
    total = N.sum(unique_counts)
    probs = unique_counts/total

    # remove probabilities==0 because log(0) = -Inf and causes problems.
    # This is ok because p*log(p) == 0*log(0) == 0 so removing these doesn't affect the final sum.
    probs = probs[probs>0] 

    return sum(-probs*N.log(probs))


def edit_distance(network1, network2):
    """Returns the edit distance between two networks.
    
    This is a good (but not the only one) metric for determining similarity
    between two networks.  
    
    """

    def inverse(edge):
        return (edge[1], edge[0])

    edges1 = copy(list(network1.edges))
    edges2 = copy(list(network2.edges))

    # Calculating distance:
    #   Add 1 to distance for every edge in one network but not in the other,
    #   EXCEPT, if inverse of edge exists in the other network, distance is 
    #   1 not 2 (this is because edit operations include add, remove and reverse)
    dist = 0
    for edge in edges1:
        if edge in edges2:
            edges2.remove(edge)
        elif inverse(edge) in edges2:
            dist += 1
            edges2.remove(inverse(edge))
        else:
            dist += 1
    
    # edges2 now contains all edges not in edges1.
    dist += len(edges2)

    return dist

def levenshtein(a,b):
    """Calculates the Levenshtein distance between *strings* a and b.

    from http://hetland.org/coding/python/levenshtein.py

    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

