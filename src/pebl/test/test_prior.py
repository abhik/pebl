"""
==================
Testing pebl.prior
==================

>>> from pebl import data, network, prior
>>> import numpy as N

Test out the null prior
------------------------

>>> net = network.Network([data.DiscreteVariable(i,3) for i in xrange(5)], "0,1;3,2;2,4")
>>> p1 = prior.NullPrior()
>>> p1.loglikelihood(net)
0.0
>>> net.edges.add((1,4))
>>> p1.loglikelihood(net)
0.0

Test out the uniform prior
--------------------------
**Note:** The uniform prior assumes equal likelihood for each edge; thus, it
penalizes networks with large number of edges.

>>> p2 = prior.UniformPrior(len(net.nodes))
>>> p2.loglikelihood(net)
-2.0
>>> net.edges.remove((1,4))
>>> p2.loglikelihood(net)
-1.5

>>> p3 = prior.UniformPrior(len(net.nodes), weight=2.0)
>>> p3.loglikelihood(net)
-3.0
>>> net.edges.add((1,4))
>>> p3.loglikelihood(net)
-4.0


Test out hard priors (constraints)
----------------------------------
>>> p4 = prior.Prior(5, edges_mustexist=[(1,4),(0,1)], edges_mustnotexist=[(3,4)], constraints=[lambda am:not am[0,4]])

>>> list(net.edges)
[(0, 1), (1, 4), (2, 4), (3, 2)]

>>> p4.loglikelihood(net)
0.0

>>> net.edges.remove((1,4))
>>> p4.loglikelihood(net)
-inf

>>> net.edges.add((1,4))
>>> net.edges.add((3,4))
>>> p4.loglikelihood(net)
-inf

>>> net.edges.remove((3,4))
>>> net.edges.add((0,4))
>>> p4.loglikelihood(net)
-inf

>>> net.edges.remove((0,4))
>>> net.edges.add((3,2))
>>> p4.loglikelihood(net)
0.0

Test out soft priors
---------------------
>>> energymat = N.ones((5,5)) * .5

>>> energymat 
array([[ 0.5,  0.5,  0.5,  0.5,  0.5],
       [ 0.5,  0.5,  0.5,  0.5,  0.5],
       [ 0.5,  0.5,  0.5,  0.5,  0.5],
       [ 0.5,  0.5,  0.5,  0.5,  0.5],
       [ 0.5,  0.5,  0.5,  0.5,  0.5]])

>>> energymat[1,4] = 0
>>> energymat[0,1] = 0
>>> energymat[3,4] = 5

>>> energymat
array([[ 0.5,  0. ,  0.5,  0.5,  0.5],
       [ 0.5,  0.5,  0.5,  0.5,  0. ],
       [ 0.5,  0.5,  0.5,  0.5,  0.5],
       [ 0.5,  0.5,  0.5,  0.5,  5. ],
       [ 0.5,  0.5,  0.5,  0.5,  0.5]])

>>> p5 = prior.Prior(5, energymat)

>>> net.edges.clear()
>>> net.edges.add_many([(0,1), (2,4), (1,2)])

>>> p5.loglikelihood(net)
-1.0

>>> net.edges.add((1,4))
>>> net.edges.remove((2,4))
>>> p5.loglikelihood(net)
-0.5

>>> net.edges.remove((1,4))
>>> net.edges.add((3,4))
>>> p5.loglikelihood(net)
-5.5

Test both soft and hard priors together
---------------------------------------

>>> p6 = prior.Prior(5, energymat, edges_mustexist=[(1,2)])

>>> net.edges.clear()
>>> net.edges.add_many([(1,2),(0,1),(1,3)])
>>> p6.loglikelihood(net)
-1.0

>>> net.edges.remove((1,2))
>>> p6.loglikelihood(net)
-inf
>>>
"""

if __name__ == '__main__':
    from pebl.test import run
    run()

