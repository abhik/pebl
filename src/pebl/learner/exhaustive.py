"""Classes and functions for doing exhaustive learning."""

from pebl import prior, config, evaluator, result, network
from pebl.learner.base import Learner
from pebl.taskcontroller.base import Task


class ListLearner(Learner):
    #
    # Parameter
    #
    _params = (
        config.StringParameter(
            'listlearner.networks',
            """List of networks, one per line, in network.Network.as_string()
            format.""", 
            default=''
        )
    )

    def __init__(self, data_=None, prior_=None, networks=None):
        """Create a ListLearner learner.

        networks should be a list of networks (as network.Network instances). 

        """

        super(ListLearner, self).__init__(data_, prior_)
        self.networks = networks
        if not networks:
            variables = self.data.variables
            _net = lambda netstr: network.Network(variables, netstr)
            netstrings = config.get('listlearner.networks').splitlines()
            self.networks = (_net(s) for s in netstrings if s)

    def run(self):
        self.result = result.LearnerResult(self)
        self.evaluator = evaluator.fromconfig(self.data, prior_=self.prior)

        self.result.start_run()
        for net in self.networks:
            self.result.add_network(net, self.evaluator.score_network(net))
        self.result.stop_run()
        return self.result
    
    def split(self, count):
        """Split the learner into multiple learners.

        Splits self.networks into `count` parts. This is similar to MPI's
        scatter functionality.
    
        """

        nets = list(self.networks)
        numnets = len(nets)
        netspertask = numnets/count

        # divide list into parts
        indices = [[i,i+netspertask] for i in xrange(0,numnets,netspertask)]
        if len(indices) > count:
            indices.pop(-1)
            indices[-1][1] = numnets-1

        return [ListLearner(self.data, self.prior, nets[i:j])for i,j in indices]

    def __getstate__(self):
        # convert self.network from iterators or generators to a list
        d = self.__dict__
        d['networks'] = list(d['networks'])
        return d
