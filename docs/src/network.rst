:mod:`network` -- Directed Acyclic Graphs
=========================================

.. module:: pebl.network
    :synopsis: datastructures and functions for dealing with networks

A pebl network is a collection of nodes and directed edges between nodes.  

Nodes are a list of pebl.data.Variable instances.
Edges are stored in EdgeList instances.  This module provides two implementations,
MatrixEdgeList for small networks and SparseEdgeList for large, sparse
networks. Both offer the same functionality with different performance
characteristics.

Functions and methods accept and return nodes as numbers representing their
indices and edges as tuples of integers corresponding to (srcnode, destnode).

Edges
-----

.. autoclass:: EdgeSet
    :members:

Network
-------

.. autoclass:: Network
    :members:

Factory functions
------------------

.. autofunction:: fromdata

.. autofunction:: random_network


