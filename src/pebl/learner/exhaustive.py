from pebl import prior, config, evaluator, result, network
from pebl.learner import Learner
from pebl.taskcontroller.base import Task


class ListLearner(Learner):
    #
    # Parameter
    #
    _pnetworks = config.StringParameter(
        'listlearner.networks',
        'List of networks to score.',
        default=''
    )

    def __init__(self, data_=None, prior_=None, iterable=None):
        super(ListLearner, self).__init__(data_, prior_)
        self.iterable = iterable
        if not self.iterable:
            _net = lambda s: network.Network(self.data.variables, s)
            netstrings = config.get('listlearner.networks').splitlines()
            self.iterable = [_net(s) for s in netstrings if s]

    def run(self):
        iterable = self.iterable
        self.result = result.LearnerResult(self)
        self.evaluator = evaluator.fromconfig(self.data, prior_=self.prior)

        self.result.start_run()
        for net in iterable:
            self.result.add_network(net, self.evaluator.score_network(net))
        self.result.stop_run()
        return self.result
    
    def toconfig(self):
        # TODO: remove this limitation:
        if not isinstance(self.prior, prior.NullPrior):
            raise Exception(
                """Currently, pebl can only generate tasks for learners with
                NullPrior priors.  This will be fixed in the next version."""
            )
        
        nets = list(self.iterable)
        configobj = super(ExactEnumerationLearner, self).toconfig()
        if not configobj.has_section('listlearner'):
            configobj.add_section('listlearner')
        configobj.set('listlearner', 'networks', 
                      '\n'.join(n.as_string() for n in nets))

        return configobj
     
    def split(self, count):
        nets = list(self.iterable)
        numnets = len(nets)
        netspertask = numnets/count

        # divide list into parts
        indices = [[i,i+netspertask] for i in xrange(0,numnets,netspertask)]
        if len(indices) > count:
            indices.pop(-1)
            indices[-1][1] = numnets-1

        return [ExactEnumerationLearner(self.data, self.prior, nets[i:j]) \
                    for i,j in indices
               ]


