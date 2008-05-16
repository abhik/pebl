r"""
=================
Testing pebl.data
=================

>>> from pebl import data
>>> from pebl.test import testfile
>>> import numpy as N

Testing basic file parsing
---------------------------

testfiles/testdata1.txt:

var1	var2	var3
2.5!	!X	1.7
1.1	    !1.7	2.3
4.2	999.3	12

>>> data1 = data.fromfile(testfile('testdata1.txt'))
>>> data1.observations
array([[   2.5,    0. ,    1.7],
       [   1.1,    1.7,    2.3],
       [   4.2,  999.3,   12. ]])

>>> data1.observations.dtype
dtype('float64')

>>> [v.name for v in data1.variables]
['var1', 'var2', 'var3']

>>> data1.missing
array([[False,  True, False],
       [False, False, False],
       [False, False, False]], dtype=bool)

>>> data1.interventions
array([[ True,  True, False],
       [False,  True, False],
       [False, False, False]], dtype=bool)

**If arity is not specified, pebl will no longer try to guess.**
>>> [v.arity for v in data1.variables]
[-1, -1, -1]


Testing a more complex file parsing example
-------------------------------------------

testfiles/testdata2.txt:

# comment line			
"shh,discrete(2)"	"ptchp,discrete(3)"	"smo,continuous"	"outcome,class(good, bad)"

0!	!0	1.25	good
#comment in the data section			
1	!1	1.1	bad
1	2	0.45	bad

>>> data2 = data.fromfile(testfile('testdata2.txt'))
>>> data2.observations
array([[ 0.  ,  0.  ,  1.25,  0.  ],
       [ 1.  ,  1.  ,  1.1 ,  1.  ],
       [ 1.  ,  2.  ,  0.45,  1.  ]])

>>> data2.interventions
array([[ True,  True, False, False],
       [False,  True, False, False],
       [False, False, False, False]], dtype=bool)

>>> data2.variables[3].labels
['good', 'bad']

>>> [v.arity for v in data2.variables]
[2, 3, -1, 2]

>>> [v.name for v in data2.variables]
['shh', 'ptchp', 'smo', 'outcome']


Testing a file with sample names
---------------------------------

testfiles/testdata3.txt:

	"shh,discrete(2)"	"ptchp,discrete(3)"
sample1	0!	!0
sample2	1	!1
sample3	1	2

>>> data3 = data.fromfile(testfile('testdata3.txt'))
>>> data3.variables
array([<DiscreteVariable: shh>, <DiscreteVariable: ptchp>], dtype=object)

>>> data3.samples
array([<Sample: sample1>, <Sample: sample2>, <Sample: sample3>], dtype=object)

>>> data3.observations
array([[0, 0],
       [1, 1],
       [1, 2]])

>>> [v.arity for v in data3.variables]
[2, 3]

Testing another file with sample names
----------------------------------------

testfiles/testdata4.txt (no tab before variable names):

"shh,discrete(2)"	"ptchp,discrete(3)"	
sample1	0!	!0
sample2	1	!1
sample3	1	2

>>> data4 = data.fromfile(testfile('testdata4.txt'))
>>> data4.variables
array([<DiscreteVariable: shh>, <DiscreteVariable: ptchp>], dtype=object)

>>> data4.observations
array([[0, 0],
       [1, 1],
       [1, 2]])


Create a data object manually and test its features
---------------------------------------------------

>>> obs = N.array([[1.2, 1.4, 2.1, 2.2, 1.1],
...                [2.3, 1.1, 2.1, 3.2, 1.3],
...                [3.2, 0.0, 2.2, 2.5, 1.6],
...                [4.2, 2.4, 3.2, 2.1, 2.8],
...                [2.7, 1.5, 0.0, 1.5, 1.1],
...                [1.1, 2.3, 2.1, 1.7, 3.2] ])
... 
>>> interventions = N.array([[0,0,0,0,0],
...                          [0,1,0,0,0],
...                          [0,0,1,1,0],
...                          [0,0,0,0,0],
...                          [0,0,0,0,0],
...                          [0,0,0,1,0] ])
... 
>>> missing = N.array([[0,0,0,0,0],
...                    [0,0,0,0,0],
...                    [0,1,0,0,0],
...                    [0,1,0,0,0],
...                    [0,0,1,0,0],
...                    [0,0,0,0,0] ])
>>> variablenames = ["gene A", "gene B", "receptor protein C", " receptor D", "E kinase protein"]
>>> samplenames = ["head.wt", "limb.wt", "head.shh_knockout", "head.gli_knockout", 
...                "limb.shh_knockout", "limb.gli_knockout"]
>>> data5 = data.Dataset(
...           obs, 
...           missing.astype(bool), 
...           interventions.astype(bool),
...           N.array([data.Variable(n) for n in variablenames]),
...           N.array([data.Sample(n) for n in samplenames])
... )


>>> data5.variables
array([<Variable: gene A>, <Variable: gene B>,
       <Variable: receptor protein C>, <Variable:  receptor D>,
       <Variable: E kinase protein>], dtype=object)

>>> data5.samples
array([<Sample: head.wt>, <Sample: limb.wt>, <Sample: head.shh_knockout>,
       <Sample: head.gli_knockout>, <Sample: limb.shh_knockout>,
       <Sample: limb.gli_knockout>], dtype=object)

>>> data5.observations
array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
       [ 2.3,  1.1,  2.1,  3.2,  1.3],
       [ 3.2,  0. ,  2.2,  2.5,  1.6],
       [ 4.2,  2.4,  3.2,  2.1,  2.8],
       [ 2.7,  1.5,  0. ,  1.5,  1.1],
       [ 1.1,  2.3,  2.1,  1.7,  3.2]])

>>> data5.subset(variables=[0,2,4]).observations
array([[ 1.2,  2.1,  1.1],
       [ 2.3,  2.1,  1.3],
       [ 3.2,  2.2,  1.6],
       [ 4.2,  3.2,  2.8],
       [ 2.7,  0. ,  1.1],
       [ 1.1,  2.1,  3.2]])

>>> data5.subset(samples=[0,2]).observations
array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
       [ 3.2,  0. ,  2.2,  2.5,  1.6]])

>>> data5.subset(variables=[0,2], samples=[1,2]).observations
array([[ 2.3,  2.1],
       [ 3.2,  2.2]])

>>> data5_subset1 = data5.subset(variables=[1,2], samples=[2,3,4])

>>> data5_subset1.observations
array([[ 0. ,  2.2],
       [ 2.4,  3.2],
       [ 1.5,  0. ]])

>>> data5_subset1.interventions
array([[False,  True],
       [False, False],
       [False, False]], dtype=bool)

>>> data5_subset1.missing
array([[ True, False],
       [ True, False],
       [False,  True]], dtype=bool)

>>> data5_subset1.variables
array([<Variable: gene B>, <Variable: receptor protein C>], dtype=object)

>>> data5_subset1.samples
array([<Sample: head.shh_knockout>, <Sample: head.gli_knockout>,
       <Sample: limb.shh_knockout>], dtype=object)

>>> data5.missing.any()
True

>>> N.where(data5.missing)
(array([2, 3, 4]), array([1, 1, 2]))

>>> data5.missing[N.where(data5.missing)]
array([ True,  True,  True], dtype=bool)

>>> N.transpose(N.where(data5.missing))
array([[2, 1],
       [3, 1],
       [4, 2]])


Try discretizing data
----------------------

testfile/testdata5.txt:

v1	v2	v3	v4	v5
1.2	1.4	2.1	2.2	1.1
2.3	1.1	2.1	3.2	1.3
3.2	0	1.2	2.5	1.6
4.2	2.4	3.2	2.1	2.8
2.7	1.5	0	1.5	1.1
1.1	2.3	2.1	1.7	3.2
2.3	1.1	4.3	2.3	1.1
3.2	2.6	1.9	1.7	1.1
2.1	1.5	3	1.4	1.1

>>> data5 = data.fromfile(testfile('testdata5.txt'))
>>> data5.discretize()

>>> [v.arity for v in data5.variables]
[3, 3, 3, 3, 3]

>>> data5.original_observations
array([[ 1.2,  1.4,  2.1,  2.2,  1.1],
       [ 2.3,  1.1,  2.1,  3.2,  1.3],
       [ 3.2,  0. ,  1.2,  2.5,  1.6],
       [ 4.2,  2.4,  3.2,  2.1,  2.8],
       [ 2.7,  1.5,  0. ,  1.5,  1.1],
       [ 1.1,  2.3,  2.1,  1.7,  3.2],
       [ 2.3,  1.1,  4.3,  2.3,  1.1],
       [ 3.2,  2.6,  1.9,  1.7,  1.1],
       [ 2.1,  1.5,  3. ,  1.4,  1.1]])

>>> data5.observations
array([[0, 1, 1, 1, 0],
       [1, 0, 1, 2, 1],
       [2, 0, 0, 2, 2],
       [2, 2, 2, 1, 2],
       [1, 1, 0, 0, 0],
       [0, 2, 1, 0, 2],
       [1, 0, 2, 2, 0],
       [2, 2, 0, 0, 0],
       [0, 1, 2, 0, 0]], dtype=int8)

**Note:** the discretization for the last column is not a maximum entropy
distribution. That is because the default discretizer maps identical input
values to identical output values. All 5 values of "1.1" in the original
dataset map to "0" even though that leads to a non maximum-entropy
distribution.

>>> data5 = data.fromfile(testfile('testdata5.txt'))

>>> data5.discretize(includevars=[0,2])

>>> data5.observations
array([[ 0. ,  1.4,  1. ,  2.2,  1.1],
       [ 1. ,  1.1,  1. ,  3.2,  1.3],
       [ 2. ,  0. ,  0. ,  2.5,  1.6],
       [ 2. ,  2.4,  2. ,  2.1,  2.8],
       [ 1. ,  1.5,  0. ,  1.5,  1.1],
       [ 0. ,  2.3,  1. ,  1.7,  3.2],
       [ 1. ,  1.1,  2. ,  2.3,  1.1],
       [ 2. ,  2.6,  0. ,  1.7,  1.1],
       [ 0. ,  1.5,  2. ,  1.4,  1.1]])

>>> data5 = data.fromfile(testfile('testdata5.txt'))

>>> data5.discretize(excludevars=[0,1])

>>> data5.observations
array([[ 1.2,  1.4,  1. ,  1. ,  0. ],
       [ 2.3,  1.1,  1. ,  2. ,  1. ],
       [ 3.2,  0. ,  0. ,  2. ,  2. ],
       [ 4.2,  2.4,  2. ,  1. ,  2. ],
       [ 2.7,  1.5,  0. ,  0. ,  0. ],
       [ 1.1,  2.3,  1. ,  0. ,  2. ],
       [ 2.3,  1.1,  2. ,  2. ,  0. ],
       [ 3.2,  2.6,  0. ,  0. ,  0. ],
       [ 2.1,  1.5,  2. ,  0. ,  0. ]])

>>> [v.arity for v in data5.variables]
[-1, -1, 3, 3, 3]


Try out the arity checking feature
----------------------------------

If the arity specified for a variable is less than the number of unique values,
pebl should raise an exception:

>>> data6 = data.fromfile(testfile('testdata6.txt'))
Traceback (most recent call last):
IncorrectArityError

If the arity specified is more than the number of unique values, that is fine:

>>> data7 = data.fromfile(testfile('testdata7.txt'))
>>> [v.arity for v in data7.variables]
[3, 4, 3, 6]

"""

if __name__ == '__main__':
    from pebl.test import run
    run()

