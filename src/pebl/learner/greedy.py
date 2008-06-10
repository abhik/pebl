"""Learner that implements a greedy learning algorithm"""

from pebl import network, result, evaluator
from pebl.util import *
from pebl.learner.base import *

class GreedyLearnerStatistics:
    def __init__(self):
        self.restarts = -1
        self.iterations = 0
        self.unimproved_iterations = 0
        self.best_score = 0
        self.start_time = time.time()

    @property
    def runtime(self):
        return time.time() - self.start_time

class GreedyLearner(Learner):
    #
    # Parameters
    #
    _params =  (
        config.IntParameter(
            'greedy.max_iterations',
            """Maximum number of iterations to run.""",
            default=1000
        ),
        config.IntParameter(
            'greedy.max_time',
            """Maximum learner runtime in seconds.""",
            default=0
        ),
        config.IntParameter(
            'greedy.max_unimproved_iterations',
            """Maximum number of iterations without score improvement before
            a restart.""", 
            default='restart_after_max_unimproved_iterations(500)'
        ),
        config.StringParameter(
            'greedy.seed',
            'Starting network for a greedy search.',
            default=''
        )
    )

    def __init__(self, data_=None, prior_=None, **options):
        """
        Create a learner that uses a greedy learning algorithm.

        The algorithm works as follows:

            1. start with a random network
            2. Make a small, local change and rescore network
            3. If new network scores better, accept it, otherwise reject.
            4. Steps 2-3 are repeated till the restarting_criteria is met, at
               which point we begin again with a new random network (step 1)
        
        Any config param for 'greedy' can be passed in via options.
        Use just the option part of the parameter name.
            
        """

        super(GreedyLearner, self).__init__(data_, prior_)
        self.options = options
        config.setparams(self, options)
        if not isinstance(self.seed, network.Network):
            self.seed = network.Network(self.data.variables, self.seed)
        
    def run(self):
        """Run the learner.

        Returns a LearnerResult instance. Also sets self.result to that
        instance.  
        
        """

        # max_time and max_iterations are mutually exclusive stopping critera
        if 'max_time' not in self.options:
            _stop = self._stop_after_iterations
        else:
            _stop = self._stop_after_time
            
        self.stats = GreedyLearnerStatistics()
        self.result = result.LearnerResult(self)
        self.evaluator = evaluator.fromconfig(self.data, self.seed, self.prior)
        self.evaluator.score_network(self.seed.copy())

        first = True
        self.result.start_run()
        while not _stop():
            self._run_without_restarts(_stop, self._restart, 
                                       randomize_net=(not first))
            first = False
        self.result.stop_run()

        return self.result

    def _run_without_restarts(self, _stop, _restart, randomize_net=True):
        self.stats.restarts += 1
        self.stats.unimproved_iterations = 0

        if randomize_net:
            self.evaluator.randomize_network()
         
        # set the default best score
        self.stats.best_score = self.evaluator.score_network()

        # continue learning until time to stop or restart
        while not (_restart() or _stop()):
            self.stats.iterations += 1

            try:
                curscore = self._alter_network_randomly_and_score()
            except CannotAlterNetworkException:
                return
            
            self.result.add_network(self.evaluator.network, curscore)

            if curscore <= self.stats.best_score:
                # score did not improve, undo network alteration
                self.stats.unimproved_iterations += 1
                self.evaluator.restore_network()
                #print '.', curscore
            else:
                self.stats.best_score = curscore
                self.stats.unimproved_iterations = 0
                #print 'X', curscore

    #
    # Stopping and restarting criteria
    # 
    def _stop_after_time(self):
        return self.stats.runtime > self.max_time

    def _stop_after_iterations(self):
        return self.stats.iterations > self.max_iterations

    def _restart(self):
        return self.stats.unimproved_iterations > self.max_unimproved_iterations

