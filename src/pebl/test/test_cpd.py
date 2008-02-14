r"""
================
Testing pebl.cpd
================


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


Now, let's try that with pebl
------------------------------

>>> from pebl import data, cpd
>>> from numpy import array

>>> nodedata = data.Dataset(array([[0, 1, 1, 0],
...                    [1, 0, 0, 1],
...                    [1, 1, 1, 0],
...                    [1, 1, 1, 0],
...                    [0, 0, 1, 1]
... ]))
>>> for v in nodedata.variables: 
...     v.arity = 2

>>> nodecpd = cpd.MultinomialCPD(nodedata)
>>> nodecpd.lnfactorial_cache
array([  0.        ,   0.        ,   0.69314718,   1.79175947,
         3.17805383,   4.78749174,   6.57925121,   8.52516136,
        10.6046029 ,  12.80182748,  15.10441257,  17.50230785,
        19.9872145 ,  22.55216385,  25.19122118,  27.89927138,  30.67186011])

>>> nodecpd.offsets
array([0, 1, 2, 4])

>>> nodecpd.counts
array([[0, 0, 0],
       [0, 0, 0],
       [0, 0, 0],
       [1, 2, 3],
       [0, 1, 1],
       [0, 0, 0],
       [1, 0, 1],
       [0, 0, 0]])

>>> nodecpd.loglikelihood()
-3.8712010109078907
>>> 


Let's alter the data (as we would when doing Gibbs sampling)
-------------------------------------------------------------

1. Let's do a NOOP replace_data to make sure it doesn't break anything

>>> nodecpd.replace_data([0,1,1,0], [0,1,1,0])
>>> nodecpd.counts
array([[0, 0, 0],
       [0, 0, 0],
       [0, 0, 0],
       [1, 2, 3],
       [0, 1, 1],
       [0, 0, 0],
       [1, 0, 1],
       [0, 0, 0]])
>>> nodecpd.loglikelihood()
-3.8712010109078907


2. Let's do a real replace data

>>> nodecpd.replace_data(nodedata.observations[0], [1,1,1,0])
>>> nodecpd.counts
array([[0, 0, 0],
       [0, 0, 0],
       [0, 0, 0],
       [0, 3, 3],
       [0, 1, 1],
       [0, 0, 0],
       [1, 0, 1],
       [0, 0, 0]])
>>> nodecpd.loglikelihood()
-2.7725887222397811


3. Can we undo without breaking something?

>>> nodecpd.replace_data([1,1,1,0],[0,1,1,0])
>>> nodecpd.counts
array([[0, 0, 0],
       [0, 0, 0],
       [0, 0, 0],
       [1, 2, 3],
       [0, 1, 1],
       [0, 0, 0],
       [1, 0, 1],
       [0, 0, 0]])
>>> nodecpd.loglikelihood()
-3.8712010109078907


4. Does it matter if we pass data as numpy.ndarray?

>>> nodecpd.replace_data(array([0,1,1,0]), array([1,1,1,0]))
>>> nodecpd.loglikelihood()
-2.7725887222397811


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


>>> newdata = data.Dataset(array([[1],
...        [0],
...        [1],
...        [1],
...        [0]])
... )

>>> newdata.variables[0].arity = 2

>>> newcpd = cpd.MultinomialCPD(newdata)

>>> newcpd.offsets
array([0])
>>> newcpd.counts
array([[2, 3, 5]])
>>> newcpd.loglikelihood()
-4.0943445622221013
>>>

"""

if __name__ == '__main__':
    from pebl.test import run
    run()



