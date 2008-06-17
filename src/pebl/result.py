"""Classes for learner results and statistics."""

from __future__ import with_statement

import time
import socket
from bisect import insort, bisect
from copy import deepcopy, copy
import cPickle
import os.path
import shutil
import tempfile

from numpy import exp

try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    import simplejson
    from pkg_resources import resource_filename
    _can_create_html = True
except:
    _can_create_html = False
    
from pebl import posterior, config
from pebl.util import flatten, rescale_logvalues
from pebl.network import Network

class _ScoredNetwork(Network):
    """A class  for representing scored networks.
    
    Supports comparision of networks based on score and equality based on first
    checking score equality (MUCH faster than checking network edges), then edges.  
 
    Note: This is a private class used by LearnerResult. It's interface is
    not guaranteed to ramain stable.

    """

    def __init__(self, edgelist, score):
        self.edges = edgelist
        self.score = score

    def __cmp__(self, other):
        return cmp(self.score, other.score)

    def __eq__(self, other):
        return self.score == other.score and self.edges == other.edges

    def __hash__(self):
        return hash(self.edges)


class LearnerRunStats:
    def __init__(self, start):
        self.start = start
        self.end = None
        self.host = socket.gethostname()

class LearnerResult:
    """Class for storing any and all output of a learner.

    This is a mutable container for networks and scores. In the future, it will
    also be the place to collect statistics related to the learning task.

    """

    #
    # Parameters
    #
    _params = (
        config.StringParameter(
            'result.filename',
            'The name of the result output file',
            default='result.pebl'
        ),
        config.IntParameter(
            'result.size',
            """Number of top-scoring networks to save. Specify 0 to indicate that
            all scored networks should be saved.""",
            default=1000
        )
    )

    def __init__(self, learner_=None, size=None):
        self.data = learner_.data if learner_ else None
        self.nodes = self.data.variables if self.data else None
        self.size = size or config.get('result.size')
        self.networks = []
        self.nethashes = {}
        self.runs = []

    def start_run(self):
        """Indicates that the learner is starting a new run."""
        self.runs.append(LearnerRunStats(time.time()))

    def stop_run(self):
        """Indicates that the learner is stopping a run."""
        self.runs[-1].end = time.time()

    def add_network(self, net, score):
        """Add a network and score to the results."""
        nets = self.networks
        nethashes = self.nethashes
        nethash = hash(net.edges)

        if self.size == 0 or len(nets) < self.size:
            if nethash not in nethashes:
                snet = _ScoredNetwork(copy(net.edges), score)
                insort(nets, snet)
                nethashes[nethash] = 1
        elif score > nets[0].score and nethash not in nethashes:
            nethashes.pop(hash(nets[0].edges))
            nets.remove(nets[0])

            snet = _ScoredNetwork(copy(net.edges), score)
            insort(nets, snet)
            nethashes[nethash] = 1

    def tofile(self, filename=None):
        filename = filename or config.get('result.filename')
        with open(filename, 'w') as fp:
            cPickle.dump(self, fp)
    
    def tohtml(self, outdir):
        if _can_create_html:
            HtmlFormatter().htmlreport(self, outdir)
        else:
            print "Cannot create html reports because some dependencies are missing."

    @property
    def posterior(self):
        return posterior.from_sorted_scored_networks(
                    self.nodes, 
                    list(reversed(self.networks))
        )


class HtmlFormatter:
    def htmlreport(self, result_, outdir, numnetworks=10):
        """Create a html report for the given result."""

        def jsonize_run(r):
            return {
                'start': time.asctime(time.localtime(r.start)),
                'end': time.asctime(time.localtime(r.end)),
                'runtime': round((r.end - r.start)/60, 3),
                'host': r.host
            }

        pjoin = os.path.join
        
        # make outdir if it does not exist
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        # copy static files to outdir
        staticdir = resource_filename('pebl', 'resources/htmlresult')
        shutil.copy2(pjoin(staticdir, 'index.html'), outdir)
        shutil.copytree(pjoin(staticdir, 'lib'), pjoin(outdir, 'lib'))
       
        # change outdir to outdir/data
        outdir = pjoin(outdir, 'data')
        os.mkdir(outdir)

        # get networks and scores
        post = result_.posterior
        numnetworks = numnetworks if len(post) >= numnetworks else len(post)
        topscores = post.scores[:numnetworks]
        norm_topscores = exp(rescale_logvalues(topscores))

        # create json-able datastructure
        resultsdata = {
            'topnets_normscores': [round(s,3) for s in norm_topscores],
            'topnets_scores': [round(s,3) for s in topscores],
            'runs': [jsonize_run(r) for r in result_.runs],
        } 

        # write out results related data (in json format)
        open(pjoin(outdir, 'result.data.js'), 'w').write(
            "resultdata=" + simplejson.dumps(resultsdata)
        )

        # create network images
        top = post[0]
        top.layout()
        for i,net in enumerate(post[:numnetworks]):
            self.network_image(
                net, 
                pjoin(outdir, "%s.png" % i), 
                pjoin(outdir, "%s-common.png" % i), 
                top.node_positions
            )

        # create consensus network images
        cm = post.consensus_matrix
        for threshold in xrange(10):
           self.consensus_network_image(
                post.consensus_network(threshold/10.0),
                pjoin(outdir, "consensus.%s.png" % threshold),
                cm, top.node_positions
            )
                
        # create score plot
        self.plot(post.scores, pjoin(outdir, "scores.png"))

    def plot(self, values, outfile):
        fig = Figure(figsize=(5,5))
        ax = fig.add_axes([0.18, 0.15, 0.75, 0.75])
        ax.scatter(range(len(values)), values, edgecolors='None',s=10)
        ax.set_title("Scores (in sorted order)")
        ax.set_xlabel("Networks")
        ax.set_ylabel("Log score")
        ax.set_xbound(-20, len(values)+20)
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure(outfile, dpi=80)

    def network_image(self, net, outfile1, outfile2, node_positions, 
                      dot="dot", neato="neato"):
        # with network's optimal layout
        fd,fname = tempfile.mkstemp()
        net.as_dotfile(fname)
        os.system("%s -Tpng -o%s %s" % (dot, outfile1, fname))
        os.remove(fname)

        # with given layout
        net.node_positions = node_positions
        fd,fname = tempfile.mkstemp()
        net.as_dotfile(fname)
        os.system("%s -n1 -Tpng -o%s %s" % (neato, outfile2, fname))
        os.remove(fname)

    def consensus_network_image(self, net, outfile, cm, node_positions):
        def colorize_edge(weight):
            colors = "9876543210"
            breakpoints = [.1, .2, .3, .4, .5, .6, .7, .8, .9]
            return "#" + str(colors[bisect(breakpoints, weight)])*6

        def node(n, position):
            s = "\t\"%s\"" % n.name
            if position:
                x,y = position
                s += " [pos=\"%d,%d\"]" % (x,y)
            return s + ";"

        nodes = net.nodes
        positions = node_positions

        dotstr = "\n".join(
            ["digraph G {"] + 
            [node(n, pos) for n,pos in zip(nodes, positions)] + 
            ["\t\"%s\" -> \"%s\" [color=\"%s\"];" % \
                (nodes[src].name, nodes[dest].name, colorize_edge(cm[src][dest])) \
                for src,dest in net.edges
            ] +
            ["}"]
        )

        fd,fname = tempfile.mkstemp()
        open(fname, 'w').write(dotstr)
        os.system("neato -n1 -Tpng -o%s %s" % (outfile, fname))
        os.remove(fname)

#
# Factory and other functions
# 
def merge(*args):
    """Returns a merged result object.

    Example::

        merge(result1, result2, result3)
        results = [result1, result2, result3]
        merge(results)
        merge(*results)
    
    """
   
    results = flatten(args)
    if len(results) is 1:
        return results[0]

    # create new result object
    newresults = LearnerResult()
    newresults.data = results[0].data
    newresults.nodes = results[0].nodes

    # merge all networks, remove duplicates, then sort
    allnets = list(set([net for net in flatten(r.networks for r in results)]))
    allnets.sort()
    newresults.networks = allnets
    newresults.nethashes = dict([(net, 1) for net in allnets])

    # merge run statistics
    if hasattr(results[0], 'runs'):
        newresults.runs = flatten([r.runs for r in results]) 
    else:
        newresults.runs = []

    return newresults

def fromfile(filename):
    """Loads a learner result from file."""

    return cPickle.load(open(filename))
