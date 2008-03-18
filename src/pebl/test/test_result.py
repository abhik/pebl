"""
===================
Testing pebl.result
===================


>>> from pebl import result
>>> from pebl import data, network
>>> from pebl.test import testfile

Test _ScoredNetwork
--------------------

>>> from pebl.result import _ScoredNetwork
>>> net = network.Network([data.Variable(x) for x in range(5)], "0,1")
>>> sn1 = _ScoredNetwork(net.edges, -11.15)
>>> net = network.Network([data.Variable(x) for x in range(5)], "1,0")
>>> sn2 = _ScoredNetwork(net.edges, -11.15)
>>> sn1 == sn2
False
>>> sn2.score = -10.0
>>> sn2 > sn1
True

Test LearnerResult
-------------------

>>> res = result.LearnerResult(size=3)
>>> res.nodes = net.nodes
>>> res.start_run()
>>> networks = ("0,1", "1,0" , "1,2;2,3", "4,1;1,2", "4,2;4,3")
>>> scores = (-10.5, -11, -8.5, -12, -13)
>>> for n,s in zip(networks, scores): res.add_network(network.Network(net.nodes, n), s)
>>> res.networks[0].score
-11
>>> len(res.networks)
3

Let's try with size=0 (all scored networks are saved)

>>> res2 = result.LearnerResult(size=0)
>>> res2.nodes = net.nodes
>>> res2.start_run()
>>> for n,s in zip(networks, scores): res2.add_network(network.Network(net.nodes, n), s)
>>> res2.networks[0].score
-13
>>> len(res2.networks)
5
>>> [n.score for n in res2.networks]
[-13, -12, -11, -10.5, -8.5]


Merging results
----------------

>>> res2.add_network(network.Network(net.nodes, "1,2;2,3;3,4"), -6)
>>> res2.add_network(network.Network(net.nodes, "1,2;2,3;3,4;0,4;0,2"), -5.5)
>>> mres = result.merge(res, res2)
>>> mres2 = result.merge([res, res2])
>>> len(mres.networks)
7
>>> len(mres2.networks)
7
>>> [n.score for n in mres.networks]
[-13, -12, -11, -10.5, -8.5, -6, -5.5]


Getting the Posterior
----------------------
>>> mpost = mres.posterior
>>> mpost[0].score
-5.5
>>> list(mpost[0].edges)
[(0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]

Testing the Posterior
---------------------
>>> len(mpost)
7
>>> mpost[0].score
-5.5
>>> mpost[:2][1].score
-6.0
>>> mpost.entropy
0.52271400039735116
>>> mpost.consensus_network(.5).as_string()
'0,2;0,4;1,2;2,3;3,4'
>>> mpost.consensus_network(.8).as_string()
'1,2;2,3;3,4'

"""

if __name__ == '__main__':
    from pebl.test import run
    run()

