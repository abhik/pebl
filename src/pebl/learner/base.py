import numpy as N

from pebl import network, config, evaluator, data, prior
from pebl.taskcontroller import Task

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
        self.prior = prior_ or prior.fromconfig()
        self.__dict__.update(kw)

        # parameters
        self.numtasks = config.get('learner.numtasks')

        # stats
        self.reverse = 0
        self.add = 0
        self.remove = 0

    def _alter_network_randomly_and_score(self):
        net = self.evaluator.network
        n_nodes = self.data.variables.size
        max_attempts = n_nodes**2

        # continue making changes and undoing them till we get an acyclic network
        for i in xrange(max_attempts):
            node1, node2 = N.random.random_integers(0, n_nodes-1, 2)    
        
            if (node1, node2) in net.edges:
                # node1 -> node2 exists, so reverse it.    
                add,remove = [(node2, node1)], [(node1, node2)]
            elif (node2, node1) in net.edges:
                # node2 -> node1 exists, so remove it
                add,remove = [], [(node2, node1)]
            else:
                # node1 and node2 unconnected, so connect them
                add,remove =  [(node1, node2)], []
            
            try:
                score = self.evaluator.alter_network(add=add, remove=remove)
            except evaluator.CyclicNetworkError:
                continue # let's try again!
            else:
                if add and remove:
                    self.reverse += 1
                elif add:
                    self.add += 1
                else:
                    self.remove += 1
                return score

        # Could not find a valid network  
        raise CannotAlterNetworkException() 

    def _all_changes(self):
        net = self.evaluator.network
        changes = []

        # edge removals
        changes.extend((None, edge) for edge in net.edges)

        # edge reversals
        reverse = lambda edge: (edge[1], edge[0])
        changes.extend((reverse(edge), edge) for edge in net.edges)

        # edge additions
        nz = N.nonzero(invert(net.edges.adjacency_matrix))
        changes.extend( ((src,dest), None) for src,dest in zip(*nz) )

        return changes


