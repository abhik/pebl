## miscellaneous utility functions

import numpy
import math
import os.path


class Struct(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

def ensure_list(c):
    if isinstance(c, list):
        return c
    elif c is None:
        return []
    else:
        return [c]
 
def cond(condition, expr1, expr2):
    if condition:
        return expr1
    else:
        return expr2


def partial(func, *leftargs):
    def f(*args):
        return func(*(leftargs + args))
    return f

# curry is a better partial. 
def curry(f,x):
    def curried_function(*args, **kw):
        return f(*((x,)+args),**kw)
    return curried_function

                
def create_counter(start=0):
    def f():
        i = start
        while True:
             yield i
             i += 1
    
    return f().next


def flatten(seq):
  lst = []
  for el in seq:
    if type(el) in [list, tuple, set]:
      lst.extend(flatten(el))
    else:
      lst.append(el)
  return lst


# normalizes values in a list.. 
def normalize(lst):
    if not isinstance(lst, numpy.ndarray):
        lst = numpy.array(lst)

    return lst/lst.sum()

def rescale_logvalues(lst):
    if not isinstance(lst, numpy.ndarray):
        lst = numpy.array(lst) 
    
    return lst - lst.max()

def rescaleAndExponentiateLogValues(lst):
    lst = numpy.array(lst)
    lst = lst - lst.max()
    lst = numpy.exp(lst)

    return lst


_LogZero = 1.0e-100
_MinLogExp = math.log(_LogZero);

def logAdd(x, y):
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

def logSum(seq, start=0):
    return reduce(logAdd, seq, start)                                                                         


def makeQuestionPngs(question_x, question_y, jobdir):
    writeQuestionPng(pydot.graph_from_edges([(question_x, question_y)], directed=True), jobdir, "q1.png")
    writeQuestionPng(pydot.graph_from_edges([(question_y, question_x)], directed=True), jobdir, "q2.png")


def writeQuestionPng(graph, jobdir, filename):
    graph.set_size("1.21, .9")
    graph.set_dpi("128")
    graph.set_ratio("fill")

    for node in graph.node_list:
        node.set_style("filled")
        node.set_fillcolor("#6699cc")

    graph.write_png(os.path.join(jobdir, filename), prog="dot")

## from webpy (webpy.org)
def autoassign(self, locals):
    """
    Automatically assigns local variables to `self`.
    Generally used in `__init__` methods, as in:

        def __init__(self, foo, bar, baz=1): autoassign(self, locals())
    """
    #locals = sys._getframe(1).f_locals
    #self = locals['self']
    for (key, value) in locals.iteritems():
        if key == 'self': 
            continue
        setattr(self, key, value)

# opposite of zip..
def unzip(l, *jj):
	if jj==():
		jj=range(len(l[0]))

	rl = [[li[j] for li in l] for j in jj] # a list of lists
	if len(rl)==1:
		rl=rl[0] #convert list of 1 list to a list
	return rl


# iterate through the lists in a nested manner.
def nestediter(lst1, lst2):
    for i in lst1:
        for j in lst2:
            yield (i,j)



def exhaustive_list(list_of_lists):
    """Given a list of lists, yield all possible combinations.

    >>> list(exhaustive_list([[0,1], [0,1,"foo"]]))
     [[0, 0], [0, 1], [0, 'foo'], [1, 0], [1, 1], [1, 'foo']]

     >>> list(exhaustive_list([[0,1], [0,1], [0,1]]))
     [[0, 0, 0],
     [0, 0, 1],
     [0, 1, 0],
     [0, 1, 1],
     [1, 0, 0],
     [1, 0, 1],
     [1, 1, 0],
     [1, 1, 1]]
    
    """

    head,rest = list_of_lists[0], list_of_lists[1:]
    if len(rest) is 0:
        for val in head:
            yield (val,)
    else:
        for val in head:
            for val2 in exhaustive_list(rest):
                yield flatten((val, val2))


def logscale_probwheel(logvalues):
    # 1) rescale by setting max value to 0 and 2) exponentiate then 3) normalize (set sum to 1)
    logvalues = logvalues - max(logvalues)
    values = numpy.exp(logvalues)
    values = values/sum(values)

    binedges = values.cumsum()
    randval = numpy.random.random()
    for i, edge in enumerate(binedges):
        if randval <= edge:
            return i


def probwheel(values, scores):
    # make sure logscores is a numpy array.
    scores = numpy.array(scores)

    # edges for bins
    binedges = scores.cumsum()
    randval = numpy.random.random()
    for value, edge in zip(values, binedges):
        if randval <= edge:
            return value
    
    # should never reach here.. but might due to rounding errors.
    return values[-1]


