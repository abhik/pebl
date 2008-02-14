from pebl import network, result, evaluator
from pebl.util import *
from pebl.learner import *

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


## returns True when stopping criteria is met
def default_stopping_criteria(stats):
    return stats.iterations > 1000

def stop_after_max_iterations(max_iterations):
    return lambda stats: stats.iterations > max_iterations

def stop_after_max_seconds(max_seconds):
    return lambda stats: stats.runtime > max_seconds

def stop_after_max_minutes(max_minutes):
    return stop_after_max_seconds(max_minutes*60)


class GreedyLearner(Learner):
    #
    # Parameters
    #
    _pstop = config.StringParameter(
        'greedy.stopping_criteria',
        """Stopping criteria for the GreedyLearner.""",
        default='default_stopping_criteria'
    )

    _pseed = config.StringParameter(
        'greedy.seed',
        'Starting network for a greedy search.',
        default=''
    )

    def __init__(self, data_=None, prior_=None, stopping_criteria=None, 
                 seed=None):
        super(GreedyLearner, self).__init__(data_, prior_)
        self.stopping_criteria = \
            stopping_criteria or \
            eval(config.get('greedy.stopping_criteria'))
        self._set_seed(seed, 'greedy.seed')

    def run(self):
        self.stats = GreedyLearnerStatistics()
        self.result = result.LearnerResult(self)
        self.evaluator = evaluator.fromconfig(self.data, self.seed, self.prior)
        stopping_criteria = self.stopping_criteria
        
        self.result.start_run()
        first = True
        while not stopping_criteria(self.stats):
            self._run_without_restarts(stopping_criteria, rndnet=False)
            first = False
        
        self.result.stop_run()
        return self.result

    def _run_without_restarts(self, stopping_criteria, rndnet=True):
        self.stats.restarts += 1
        if rndnet:
            self.evaluator.randomize_network()
        
        # set the default best score
        self.stats.best_score = self.evaluator.score_network()

        # continue learning till the stopping criteria is met (function returns True)
        while not stopping_criteria(self.stats):
            self.stats.iterations += 1

            try:
                curscore = self._alter_network_randomly_and_score()
            except CannotAlterNetworkException:
                return
            
            self.result.add_network(self.evaluator.network, curscore)

            if curscore < self.stats.best_score:
                # score did not improve, undo network alteration
                self.stats.unimproved_iterations += 1
                self.evaluator.restore_network()
            else:
                self.stats.best_score = curscore
                self.stats.unimproved_iterations = 0
 

