# Want code to be py2.4 compatible. So, can't use relative imports.
import sys
sys.path.insert(0, "../")

import os

# set numpy.test to None so we don't run numpy's tests.
from numpy import *
test = None

import network
import data


class TestSparseEdgeList:
    # Which class of edgelist to use
    edgelist_class = network.SparseEdgeList

    def setUp(self):
        self.edges = self.edgelist_class(num_nodes=6)
        self.tuplelist = [(0,2), (0,5), (1,2)]
        for edge in self.tuplelist:
            self.edges.add(edge)
        
    def test_edgeiter(self):
        assert set(self.edges) == set(self.tuplelist), "Can use edgelist as an iterable object."
    
    def test_addedges1(self):
        self.edges.add((0, 3))
        assert (0,3) in self.edges, "Can add edges to edgelist."

    def test_incoming(self):
        assert self.edges.incoming(0) == [], "Testing edgelist.incoming"
        assert set(self.edges.incoming(2)) == set([0,1]), "Testing edgelist.incoming"
    
    def test_outgoing(self):
        assert self.edges.outgoing(2) == [], "Testing edgelist.outgoing"
        assert set(self.edges.outgoing(0)) == set([2,5]), "Testing edgelist.outgoing"
    
    def test_parents(self):
        assert self.edges.parents(0) == [], "Testing edgelist.parents"
        assert set(self.edges.parents(2)) == set([0,1]), "Testing edgelist.parents"
    
    def test_children(self):
        assert self.edges.children(2) == [], "Testing edgelist.children"
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
        assert (self.edges.adjacency_matrix == array(expected, dtype=bool)).all(), "Testing boolean matrix representation."


class TestMatrixEdgeList(TestSparseEdgeList):
    # Which class of edgelist to use
    edgelist_class = network.MatrixEdgeList


class TestNodeList:
    def setUp(self):
        nodes = [network.Node(0, "Foo"), network.Node(1, "Foobar"), network.Node(2, "bar"), network.Node(3, "Node X", hidden=True)]
        self.nodes = network.NodeList(nodes)

    def test_num_hiddennodes(self):
        assert self.nodes.num_hiddennodes == 1, "Checking number of hidden nodes."

    def test_slicing(self):
        assert hasattr(self.nodes[:2], 'byname'), "Slices of NodeList should be NodeList instances."

    def test_indexing(self):
        assert not hasattr(self.nodes[2], 'byname'), "NodeList.__getitem__ should return items, not NodeLists."

    def test_add(self):
        self.nodes.add(network.Node(9, "Node XX"))
        assert len(self.nodes) == 5, "Adding to NodeList"

    def test_remove(self):
        self.nodes.remove(self.nodes[2])
        assert len(self.nodes) == 3, "Removing from NodeList."

    def test_byname_simple(self):
        assert self.nodes.byname("Foo").id == 0, "Using byname to retrieve a node."

    def test_byname_multiple(self):
        nodes = self.nodes.byname(["Foo", "Foobar"])
        nodeids = [n.id for n in nodes]
        assert nodeids == [0,1], "Using byname to retrieve multiple nodes."

    def test_byname_regexp(self):
        nodes = self.nodes.byname(namelike="bar")
        nodeids = [n.id for n in nodes]
        assert nodeids == [1,2], "Using byname to retrieve nodes using regexps."

class TestNetwork:
    def setUp(self):
        self.net = network.Network()
        for node in [ network.Node(id=0, name="NodeA"),
                      network.Node(1, "NodeB"),
                      network.Node(2),
                      network.Node(3, "Hidden1", hidden=True)]:
            self.net.nodes.add(node)

        self.net.finalize_nodelist()
        for edge in [(0,1), (0,3), (1,2)]:
            self.net.edges.add(edge)

    def test_loopchecking_on_acyclic_net(self):
        assert self.net.is_acyclic(), "Network is acyclic."

    def test_loopchecking_on_cyclic_net(self):
        self.net.edges.add((2,0))
        assert not self.net.is_acyclic(), "Network should be cyclic."

    def test_randomize(self):
        self.net.randomize()
        assert self.net.is_acyclic(), "Random network should be acyclic."

    def test_num_hiddennodes(self):
        assert self.net.nodes.num_hiddennodes == 1, "Checking number of hidden nodes."

    def test_as_pydot(self):
        assert len(self.net.as_pydot().edge_list) == 3, "Can convert to pydot graph instance."

    # We can only check whether the image is created or not. Cannot check if it is correct.
    def test_as_image(self):
        filename = "testnet.png"
        self.net.as_image(filename=filename)
        file_exists = filename in os.listdir(".") 
        if file_exists:
            os.remove("./" + filename)
        
        assert file_exists, "Can create image file."

class TestFromData:
    def setUp(self):
        a = array([[1.2, 1.4, 2.1, 2.2, 1.1],
                   [2.3, 1.1, 2.1, 3.2, 1.3],
                   [3.2, 0.0, 2.2, 2.5, 1.6],
                   [4.2, 2.4, 3.2, 2.1, 2.8],
                   [2.7, 1.5, 0.0, 1.5, 1.1],
                   [1.1, 2.3, 2.1, 1.7, 3.2]
        ])

        self.data = data.PeblData(a.shape, buffer=a, dtype=a.dtype)
        self.data.missingvals = array([[0,0,0,0,1],
                                       [0,0,0,0,1],
                                       [0,1,0,0,1],
                                       [0,1,0,0,1],
                                       [0,0,1,0,1],
                                       [0,0,0,0,1] ])
        self.data._calculate_arities()
        self.data.variablenames = ["gene A", "gene B", "", " receptor D", "E kinase protein"]
        self.net = network.fromdata(self.data)

    def test_basic(self):
        assert self.net, "Check that network object was created."

    def test_nodes(self):
        assert len(self.net.nodes) == 5, "Check that all nodes were created."

    def test_nodename(self):
        assert self.net.nodes[0].name == "gene A", "Node name extracted from variable name."

    def test_nodename_when_notgiven(self):
        assert self.net.nodes[2].name == "2", "Node name defaults to node's id."

    def test_hiddennode(self):
        assert self.net.nodes[4].hidden, "Node should be a hidden node."

