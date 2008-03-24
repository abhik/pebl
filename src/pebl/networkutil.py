"""Utilities for dealing with networks."""

import numpy as N

#
# Cycle checkers
#
class CycleChecker(object):
    """Checks whether a network contains a cycle."""

    def __init__(self, network):
        self.network = network


class DFSCycleChecker(CycleChecker):
    """Uses a depth-first search (dfs) to detect cycles."""

    def _isacyclic(self, rootnodes, seen):
        edges = self.network.edges

        if rootnodes.intersection(seen):
            # already seen a node we need to visit. thus, cycle!
            return False
        
        for node in rootnodes:
            # check children for cycles
            if not self._isacyclic(set(edges.children(node)), seen.union([node])):
                return False

        # got here without returning false, so no cycles below rootnodes
        return True

    def __call__(self, roots=None):
        roots = roots if roots else set(range(len(self.network.nodes)))
        return self._isacyclic(roots, set())


class EigenValueCycleChecker(CycleChecker):
    """Uses eigenvalues to detect cycles.
    
   
    This method is fast for small networks but much slower for larger networks.
    This may be removed in future versions of Pebl.
        
    """

    def __call__(self, rootnodes=None):
        edges = self.network.edges

        # first check for self-loops (1 along diagonal)
        if edges.adjacency_matrix.diagonal().any():
            return False

        # network is acylcic IFF all eigenvalues of adjacency matrix are
        # positive and real
        try:
            ev = N.linalg.eigvals(edges.adjacency_matrix)
        except:
            # the eigenvalue calculation sometimes fails to converge
            # so, create and use a DFSCycleChecker
            return DFSCycleChecker(self.network)()

        if N.any(ev[N.iscomplex(ev) == True]):
            # complex eigenvalues, so not acyclic
            return False
        else:
            # all eigenvalues positive?
            return not N.any(ev[N.signbit(ev) == True])

#
# Network randomizers
#
class NetworkRandomizer(object):
    """Creates a random network."""

    def __init__(self, network):
        self.network = network

class NaiveNetworkRandomizer(NetworkRandomizer):
    """Create a random network using a random adjacency matrix."""
    
    def __call__(self):
        n_nodes = len(self.network.nodes)
        density = 1.0/n_nodes
        max_attempts = 50

        for attempt in xrange(max_attempts):
            # create an adjacency matrix with given density
            adjmat = N.random.rand(n_nodes, n_nodes)
            adjmat[adjmat >= (1.0-density)] = 1
            adjmat[adjmat < 1] = 0
            
            # remove self-loop edges (those along the diagonal)
            adjmat = N.invert(N.identity(n_nodes).astype(bool))*adjmat
            
            # set the adjaceny matrix and check for acyclicity
            # sparse-change
            self.network.edges.adjacency_matrix = adjmat.astype(bool)
            #self.network.edges.clear()
            #for src, dest in zip(*N.nonzero(adjmat)):
                #self.network.edges.add((src,dest))

            if self.network.is_acyclic():
                return

        # got here without finding a single acyclic network.
        # so try with a less dense network
        return self.__call__(density/2)


