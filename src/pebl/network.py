"""Classes for representing networks and functions to create/modify them.

A pebl network is a collection of nodes and directed edges between nodes.  

Nodes are a list of pebl.data.Variable instances.
Edges are stored in EdgeList instances.  This module provides two implementations,
MatrixEdgeList for small networks and SparseEdgeList for large, sparse
networks. Both offer the same functionality with different performance
characteristics.

Functions and methods accept and return nodes as numbers representing their
indices and edges as tuples of integers corresponding to (srcnode, destnode).

"""

import re
import tempfile
import subprocess
import os
from copy import copy

import pydot
import numpy as N

from pebl.util import *
from pebl.networkutil import *
from pebl import config
from pebl.config import StringParameter, oneof

#
# Classes for storing collection of edges
#
class EdgeList(object):   
    """Abstract base class for collection of edges."""

    def __init__(self, num_nodes=0): pass

    def clear(self): 
        """Clear the list of edges."""
        pass
    
    def add(self, edge):
        """Add an edge to the list."""
        pass
    
    def add_many(self, edges):
        """Add multiple edges."""
        for edge in edges:
            self.add(edge)

    def remove(self, edge): 
        """Remove edges from edgelist.
        
        If an edge to be removed does not exist, fail silently (no exceptions).

        """
        pass
        
    def remove_many(self, edges):
        """Remove multiple edges."""
        for edge in edges:
            self.remove(edge)

    def incoming(self, node): 
        """Return list of nodes (as node indices) that have an edge to given node.
        
        Method is also aliased as parents().
        
        """

        pass

    def outgoing(self, node): 
        """Return list of nodes (as node indices) that have an edge from given node.
        
        Method is also aliased as children().

        """
        pass

    children = outgoing
    parents = incoming
   
    def __iter__(self): 
        """Iterate through the edges in this edgelist.

        Sample usage:
        for edge in edgelist: 
            print edge

        """
        pass

    def __contains__(self, edge):
        """Check whether an edge exists in the edgelist.


        Sample usage:
        if (4,5) in edgelist: 
            print "edge exists!"

        """

        # This is the naive implementation.  
        # Subclasses should implement more efficient versions based on their
        # internal datastructures.
        for selfedge in self:
            if edge == selfedge:
                return True

    def __eq__(self, other):
        return self.nodes == other.nodes and self.edges == other.edges

    def __len__(self):
        pass


class SparseEdgeList(EdgeList):
    """
    Maintains list of edges in two lists (for incoming and outgoing edges).

    Performance characteristics:
        - Edge insertion: O(1)
        - Edge retrieval: O(n)
    
    If we didn't maintain two indices, retrieving an edge could take O(n^2) instead of O(n).
    
    For method documentation, see documentation for EdgeList.

    """

    def __init__(self, num_nodes=0, adjacency_matrix=None):
        num_nodes = len(adjacency_matrix) if adjacency_matrix is not None else num_nodes

        self._outgoing = [[] for i in xrange(num_nodes)]
        self._incoming = [[] for i in xrange(num_nodes)] 


        if adjacency_matrix is not None:
            for src, dest in zip(*N.nonzero(self.adjacency_matrix)):
                self._outgoing[src].append(dest)
                self._incoming[dest].append(src)

    def _resize(self, num_nodes):
        """Resize the internal indices."""

        self._incoming.extend([] for i in xrange(len(self._incoming), num_nodes))
        self._outgoing.extend([] for i in xrange(len(self._outgoing), num_nodes))

    def clear(self):
        self._incoming = [[] for i in xrange(len(self._incoming))]
        self._outgoing = [[] for i in xrange(len(self._outgoing))]

    def add(self, edge):
        src,dest = edge

        if dest not in self._outgoing[src]:
            self._outgoing[src].append(dest)
        if src not in self._incoming[dest]:
            self._incoming[dest].append(src)
        
    def remove(self, edge):
        src,dest = edge
        try: 
            self._incoming[dest].remove(src)
            self._outgoing[src].remove(dest)
        except ValueError: 
            pass

    def incoming(self, node):
        return self._incoming[node]

    def outgoing(self, node):
        return self._outgoing[node]

    parents = incoming
    children = outgoing

    def __iter__(self):
        for src, dests in enumerate(self._outgoing):
            for dest in dests:
                yield (src, dest)

    @property
    def adjacency_matrix(self):
        size = len(self._outgoing)
        edges = N.zeros((size, size), dtype=bool)
       
        selfedges = list(self)
        if selfedges:
            edges[unzip(selfedges)] = True

        return edges
    
    def __contains__(self, edge):
        src, dest = edge

        try:
            return dest in self._outgoing[src]
        except IndexError:
            return False

    def __len__(self):
        return sum(len(out) for out in self._outgoing)


class MatrixEdgeList(EdgeList):
    """
    Maintains list of edges in a boolean adjacency matrix.

    Performance characteristics:
        - Edge insertion: O(1)
        - Edge retrieval: O(1)

    Memory requirements might be deemed too high for sparse networks with a large number of nodes.
    
    For method documentation, see documentation for EdgeList.

    """

    def __init__(self, num_nodes=0, adjacency_matrix=None):
        if adjacency_matrix is not None:
            self.adjacency_matrix = adjacency_matrix
        else:
            self.adjacency_matrix = N.zeros((num_nodes, num_nodes), dtype=bool)
        
    def _resize(self, num_nodes):
        newedges = N.zeros((num_nodes, num_nodes), dtype=bool)
        old_num_nodes = self.adjacency_matrix.shape[0]

        for i in range(old_num_nodes):
            for j in range(old_num_nodes):
                newedges[i][j] = self.adjacency_matrix[i][j]

        self.adjacency_matrix = newedges

    def clear(self):
        self.adjacency_matrix = N.zeros(self.adjacency_matrix.shape, dtype=bool)

    def add(self, edge):
        self.adjacency_matrix[edge] = True

    def remove(self, edge):
        try: 
            self.adjacency_matrix[edge] = False
        except ValueError:
            pass # if edge does not exist, ignore error silently.

    def incoming(self, node):
        return self.adjacency_matrix[:,node].nonzero()[0].tolist()

    def outgoing(self, node):
        return self.adjacency_matrix[node].nonzero()[0].tolist()
    
    parents = incoming
    children = outgoing

    def __iter__(self):
        for src, dest in zip(*N.nonzero(self.adjacency_matrix)):
            yield (src, dest)
    
    def __contains__(self, edge): 
        try:
            return self.adjacency_matrix[edge]
        except:
            return False
    
    def __eq__(self, other):
        return (self.adjacency_matrix == other.adjacency_matrix).all()

    def __len__(self):
        return self.adjacency_matrix.nonzero()[0].size


class MatrixEdgeList__PythonListImplementation(MatrixEdgeList):
    def __init__(self, num_nodes=0, adjacency_matrix=None):
        self.num_nodes = num_nodes or len(adjacency_matrix)
        if adjacency_matrix is not None:
            self.adjacency_matrix = adjacency_matrix
        else:
            self.adjacency_matrix = [[False for i in xrange(num_nodes)] for j in xrange(num_nodes)]
        
    def _resize(self, num_nodes):
        self.adjacency_matrix = [[False for i in xrange(num_nodes)] for j in xrange(num_nodes)]

    def clear(self):
        num_nodes = self.num_nodes
        self.adjacency_matrix = [[False for i in xrange(num_nodes)] for j in xrange(num_nodes)]
        
    def add(self, edge):
        self.adjacency_matrix[edge[0]][edge[1]] = True

    def remove(self, edge):
        self.adjacency_matrix[edge[0]][edge[1]] = False

    def incoming(self, node):
       return [i for i in xrange(self.num_nodes) if self.adjacency_matrix[i][node]]

    def outgoing(self, node):
       return [i for i in xrange(self.num_nodes) if self.adjacency_matrix[node][i]]

    parents = incoming
    children = outgoing

    def __iter__(self):
        am = self.adjacency_matrix
        nodes = range(self.num_nodes)
        return ((i,j) for i in nodes for j in nodes if am[i][j]) 

    def __contains__(self, edge): 
        try:
            return self.adjacency_matrix[edge[0]][edge[1]]
        except:
            return False

    def __eq__(self, other):
        self.adjacency_matrix == other.adjacency_matrix

    def __len__(self):
        return sum(row.count(True) for row in self.adjacency_matrix)


#
# Pebl's network class
#
class Network(object):
    """ A network is a collection of edges between nodes."""
    
    #
    # Parameters
    #
    cyclechecker = StringParameter(
        'network.cyclechecker',
        'Algorithm to determine whether a network contains a cycle.',
        oneof('dfs', 'eigenvalue'),
        'dfs'
    )

    randomizer = StringParameter(
        'network.randomizer',
        'Algorithm for generating radmon networks.',
        oneof('naive', 'chain'),
        'naive'
    )
   
    #
    # Class variables
    #
    cyclecheckers = {
        'dfs': DFSCycleChecker,
        'eigenvalue': EigenValueCycleChecker
    }

    randomizers = {
        'naive': NaiveNetworkRandomizer
    }


    #
    # Public methods
    #
    def __init__(self, nodes, edges=None):
        """Creates a Network.

        nodes is a list of pebl.data.Variable instances.
        edges can be:
            * any EdgeList instance
            * a list of edge tuples
            * an adjacency matrix (as boolean numpy.ndarray)
            * string representation (see Network.as_string() for format)

        """
        
        self.nodes = nodes

        # add edges
        if isinstance(edges, EdgeList):
            self.edges = edges
        elif isinstance(edges, N.ndarray):
            self.edges = MatrixEdgeList(adjacency_matrix=edges)
        else:
            self.edges = MatrixEdgeList(num_nodes=len(self.nodes))
            if isinstance(edges, list):
                self.edges.add_many(edges)
            elif isinstance(edges, str) and edges:
                edges = edges.split(';')
                edges = [tuple([int(n) for n in e.split(',')]) for e in edges]
                self.edges.add_many(edges)

        # select implementation for self.is_acyclic()
        cyclechecker = config.get('network.cyclechecker')
        self.is_acyclic = self.cyclecheckers[cyclechecker](self)
        
        # select implementation for self.randomize()
        randomizer = config.get('network.randomizer')
        self.randomize = self.randomizers[randomizer](self)
        
    
    # TODO: test
    def copy(self):
        """Returns a copy of this network."""
        return Network(self.nodes, self.edges.adjacency_matrix.copy())    
       

    def layout(self, width=400, height=400, dotpath="dot"): 
        """Determines network layout using Graphviz's dot algorithm.

        width and height are in pixels.
        dotpath is the path to the dot application.

        The resulting node positions are saved in network.node_positions.

        """


        tempdir = tempfile.mkdtemp(prefix="pebl")
        dot1 = os.path.join(tempdir, "1.dot")
        dot2 = os.path.join(tempdir, "2.dot")
        self.as_dotfile(dot1)

        try:
            os.system("%s -Tdot -Gratio=fill -Gdpi=60 -Gfill=10,10 %s > %s" % (dotpath, dot1, dot2))
        except:
            raise Exception("Cannot find the dot program at %s." % dotpath)

        dotgraph = pydot.graph_from_dot_file(dot2)
        nodes = (n for n in dotgraph.get_node_list() if n.get_pos())
        self.node_positions = [[int(i) for i in n.get_pos().split(',')] for n in nodes] 


    def as_string(self):
        """Returns the sparse string representation of network.

        If network has edges (2,3) and (1,2), the sparse string representation
        is "2,3;1,2".

        """

        return ";".join([",".join([str(n) for n in edge]) for edge in list(self.edges)])
       
    
    def as_dotstring(self):
        """Returns network as a dot-formatted string"""

        def node(n, position):
            s = "\t\"%s\"" % n.name
            if position:
                x,y = position
                s += " [pos=\"%d,%d\"]" % (x,y)
            return s + ";"


        nodes = self.nodes
        positions = self.node_positions if hasattr(self, 'node_positions') \
                                        else [None for n in nodes]

        return "\n".join(
            ["digraph G {"] + 
            [node(n, pos) for n,pos in zip(nodes, positions)] + 
            ["\t\"%s\" -> \"%s\";" % (nodes[src].name, nodes[dest].name) 
                for src,dest in self.edges] +
            ["}"]
        )
 

    def as_dotfile(self, filename):
        """Saves network as a dot file."""

        f = file(filename, 'w')
        f.write(self.as_dotstring())
        f.close()


    def as_pydot(self):
        """Returns a pydot instance for the network."""

        return pydot.graph_from_dot_data(self.as_dotstring())


    def as_image(self, filename, decorator=lambda x: x, prog='dot'):
        """Creates an image (PNG format) for the newtork.

        decorator is a function that accepts a pydot graph, modifies it and
        returns it.  decorators can be used to set visual appearance of
        networks (color, style, etc).

        prog is the Graphviz program to use (default: dot).

        """
        
        g = self.as_pydot()
        g = decorator(g)
        g.write_png(filename, prog=prog)


#        
# Factory functions
#
def fromdata(data_):
    """Creates a network from the variables in the dataset."""
    return Network(data_.variables)

