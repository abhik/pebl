import os
import numpy as N
from pebl import network, data, config

#
# Testing edgesets (working with edges)
#
class TestEdgeSet:
    def setUp(self):
        self.edges = network.EdgeSet(num_nodes=6)
        self.tuplelist = [(0,2), (0,5), (1,2)]
        for edge in self.tuplelist:
            self.edges.add(edge)
    
    def test_add(self):
        self.edges.add((5,1))
        assert set(self.edges) == set(self.tuplelist + [(5,1)])

    def test_add_many(self):
        self.edges.add_many([(5,1), (5,2)])
        assert set(self.edges) == set(self.tuplelist + [(5,1), (5,2)])

    def test_remove(self):
        self.edges.remove((0,2))
        assert set(self.edges) == set([(0,5), (1,2)])

    def test_remove_many(self):
        self.edges.remove_many([(0,2), (0,5)])
        assert set(self.edges) == set([(1,2)])

    def test_edgeiter(self):
        assert set(self.edges) == set(self.tuplelist), "Can use edgelist as an iterable object."

    def test_len(self):
        assert len(self.edges) == len(self.tuplelist), "Can determine number of edges"

    def test_addedges1(self):
        self.edges.add((0, 3))
        assert (0,3) in self.edges, "Can add edges to edgelist."

    def test_incoming(self):
        assert set(self.edges.incoming(0)) == set([]), "Testing edgelist.incoming"
        assert set(self.edges.incoming(2)) == set([0,1]), "Testing edgelist.incoming"
    
    def test_outgoing(self):
        assert set(self.edges.outgoing(2)) == set([]), "Testing edgelist.outgoing"
        assert set(self.edges.outgoing(0)) == set([2,5]), "Testing edgelist.outgoing"
    
    def test_parents(self):
        assert set(self.edges.parents(0)) == set([]), "Testing edgelist.parents"
        assert set(self.edges.parents(2)) == set([0,1]), "Testing edgelist.parents"
    
    def test_children(self):
        assert set(self.edges.children(2)) == set([]), "Testing edgelist.children"
        assert set(self.edges.children(0)) == set([2,5]), "Testing edgelist.children"

    def test_contains1(self):
        assert (0,2) in self.edges, "Can check if edge in edgelist."

    def test_contains2(self):
        # Should return false without throwing exception.
        assert (99,99) not in self.edges , "Edge not in edgelist."

    def test_remove(self):
        self.edges.remove((0,2))
        assert set(self.edges) == set([(0,5), (1,2)]), "Can remove an edge."

    def test_clear(self):
        self.edges.clear()
        assert list(self.edges) == [], "Can clear edgelist."

    def test_adjacency_matrix(self):
        expected = [
            [0,0,1,0,0,1],
            [0,0,1,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
        ]
        assert (self.edges.adjacency_matrix == N.array(expected, dtype=bool)).all(), "Testing boolean matrix representation."


#
# Testing is_acyclic
#
class TestIsAcyclic:
    def setUp(self):
        self.net = network.Network([data.DiscreteVariable(i,3) for i in xrange(6)])
        for edge in [(0,1), (0,3), (1,2)]:
            self.net.edges.add(edge)
    
    def test_loopchecking(self):
        assert self.net.is_acyclic(), "Should be acyclic"

    def test_loopchecking2(self):
        self.net.edges.add((2,0))
        assert not self.net.is_acyclic(), "Should not be acyclic"
    


#
# Testing network features (misc methods)
#
class TestNetwork:
    expected_dotstring = """digraph G {\n\t"0";\n\t"1";\n\t"2";\n\t"3";\n\t"4";\n\t"5";\n\t"0" -> "1";\n\t"0" -> "3";\n\t"1" -> "2";\n}"""
    expected_string = '0,1;0,3;1,2'

    def setUp(self):
        self.net = network.Network([data.DiscreteVariable(i,3) for i in xrange(6)])
        for edge in [(0,1), (0,3), (1,2)]:
            self.net.edges.add(edge)

    def test_as_pydot(self):
        assert len(self.net.as_pydot().get_edges()) == 3, "Can convert to pydot graph instance."

    # We can only check whether the image is created or not. Cannot check if it is correct.
    def test_as_image(self):
        filename = "testnet.png"
        self.net.as_image(filename=filename)
        file_exists = filename in os.listdir(".") 
        if file_exists:
            os.remove("./" + filename)
        
        assert file_exists, "Can create image file."

    def test_as_dotstring(self):
        assert self.net.as_dotstring() == self.expected_dotstring, "Create dot-formatted string"

    def test_as_dotfile(self):
        self.net.as_dotfile('testdotfile.txt')
        assert open('testdotfile.txt').read() == self.expected_dotstring, "Create dotfile."

    def test_as_string(self):
        assert self.net.as_string() == self.expected_string, "Create string representation."

    def test_layout(self):
        """net.layout() should either raise an exception or do the layout."""

        try:
            self.net.layout()
        except:
            return

        assert hasattr(self.net, 'node_positions'), "Has node_positions"
        assert len(self.net.node_positions[0]) == 2, "Node positions are 2 values (x and y)"
        assert isinstance(self.net.node_positions[0][0], (int, float)), "Positions are in floats or ints"


#
# Test constructor and factory funcs
#
class TestNetworkFromListOfEdges:
    def setUp(self):
        self.net = network.Network(
            [data.DiscreteVariable(str(i),3) for i in xrange(6)],
            [(0,1), (4,5), (2,3)]
        )

    def test_number_of_edges(self):
        assert len(list(self.net.edges)) == 3

    def test_edges_exist(self):
        assert (0,1) in self.net.edges and \
               (4,5) in self.net.edges and \
               (2,3) in self.net.edges

class TestNetworkFromString(TestNetworkFromListOfEdges):
    def setUp(self):
        self.net = network.Network(
            [data.DiscreteVariable(str(i),3) for i in xrange(6)],
            "0,1;4,5;2,3"
        )

class TestRandomNetwork:
    def setUp(self):
        self.nodes = [data.DiscreteVariable(str(i),3) for i in xrange(6)]

    def test_acyclic(self):
        net = network.random_network(self.nodes)
        assert net.is_acyclic() == True, "Random network is acyclic."

    def test_required_edges(self):
        net = network.random_network(self.nodes, required_edges=[(0,1), (3,0)])
        assert net.is_acyclic() == True and \
               (0,1) in net.edges and \
               (3,0) in net.edges

    def test_prohibited_edges(self):
        net = network.random_network(self.nodes, prohibited_edges=[(0,1), (3,0)])
        assert net.is_acyclic() == True and \
               (0,1) not in net.edges and \
               (3,0) not in net.edges

    def test_required_and_prohibited_edges(self):
        net = network.random_network(self.nodes, required_edges=[(0,1), (3,0)],
                                     prohibited_edges=[(2,3), (1,4)])

        assert net.is_acyclic() == True and \
               (0,1) in net.edges and \
               (3,0) in net.edges and \
               (2,3) not in net.edges and \
               (1,4) not in net.edges

