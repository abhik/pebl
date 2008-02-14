## For our task (learning bayesian network structure) the learner is obviously the main object.
## Learners take parameters, data, priors and a network and return a (approximated) posterior 

import time
import socket
import cPickle
import inspect
from copy import deepcopy
import sys, os, os.path

import numpy as N

from pebl import network, config, evaluator, data, prior
from pebl.taskcontroller import Task
from pebl.util import unzip

#
# Exceptions
#
class CannotAlterNetworkException(Exception):
    pass

#
# Module parameters
#
_plearnertype = config.StringParameter(
    'learner.type',
    """Type of learner to use. 

    The following learners are included with pebl:
        * greedy.GreedyLearner
        * simanneal.SimulatedAnnealingLearner
        * exhaustive.ListLearner
    """,
    default = 'greedy.GreedyLearner'
)

_ptasks = config.IntParameter(
    'learner.numtasks',
    "Number of learner tasks to run.",
    config.atleast(0),
    default=1
)



class Learner(Task):
    def __init__(self, data_=None, prior_=None, **kw):
        self.data = data_ or data.fromconfig()
        self.network = network.fromdata(data_)
        self.prior = prior_ or prior.fromconfig()
        self.__dict__.update(kw)

        # parameters
        self.numtasks = config.get('learner.numtasks')

    def _alter_network_randomly_and_score(self):
        n_nodes = self.data.variables.size
        max_attempts = n_nodes**2

        # continue making changes and undoing them till we get an acyclic network
        for i in xrange(max_attempts):
            startnode, endnode = N.random.random_integers(0, n_nodes-1, 2)    
        
            if (startnode, endnode) in self.network.edges:
                # start_node -> end_node already exists, so reverse it.    
                add,remove = [(startnode, endnode)], [(endnode, startnode)]
            elif (endnode, startnode) in self.network.edges:
                # start_node <- end_node exists, so remove it
                add,remove = [], [(endnode, startnode)]
            else:
                # start_node and end_node unconnected, so connect them
                add,remove =  [(startnode, endnode)], []
            
            try:
                return self.evaluator.alter_network(add=add, remove=remove)
            except evaluator.CyclicNetworkError:
                continue

        # Could not find a valid network after 100 attempts  
        raise CannotAlterNetworkException() 

    def _all_changes(self):
        changes = []

        # edge removals
        changes.extend((None, edge) for edge in self.network.edges)

        # edge reversals
        reverse = lambda edge: (edge[1], edge[0])
        changes.extend((reverse(edge), edge) for edge in self.network.edges)

        # edge additions
        nz = nonzero(invert(self.network.edges.adjacency_matrix))
        changes.extend( ((src,dest), None) for src,dest in zip(*nz) )

        return changes

    def _set_seed(self, seed, paramname):
        configseed = config.get(paramname)
        if seed:
            self.seed = seed
        elif configseed:
            self.seed = network.Network(self.network.nodes, configseed)
        else:
            self.network.randomize()
            self.seed = self.network

    def toconfig(self):
        params = inspect.getmembers(self, lambda x: isinstance(x, config.Parameter))
        params = dict((p.name, p.value) for p in unzip(params,1))
        params['data.text'] = self.data.tostring()


        if is_customlearner(config.get('learner.type')):
            # serializing a custom learner
            params['learner.type'] =  config.get('learner.type')
        else:
            # learner is part of pebl.learner package
            lclass = self.__class__.__name__
            lmodule = self.__module__.split('.')[-1]
            params['learner.type'] = "%s.%s" % (lmodule, lclass)

        # TODO: remove this limitation
        if not isinstance(self.prior, prior.NullPrior):
            raise Exception(
                """Currently, pebl can only generate tasks for learners with
                NullPrior priors.  This will be fixed in the next version."""
            )

        return config.configobj(params)


#TODO: test
def fromconfig(data_=None):
    learnertype = config.get('learner.type')

    if ':' in learnertype:
        cfile,learnerclass = learnertype.split(':')

        cdir,cfile = os.path.dirname(cfile),os.path.basename(cfile)
        cmod = cfile.split('.')[0]
        sys.path.insert(0, cdir)
        mymod = __import__(cmod, fromlist=['.'], )
    else:
        learnermodule,learnerclass = learnertype.split('.')
        mymod = __import__("pebl.learner.%s" % learnermodule, fromlist=['pebl.learner'])

    mylearner = getattr(mymod, learnerclass)
    return mylearner(data_ or data.fromconfig())

