from pebl import network, distributions, result
import scorer
from __init__ import *
from pebl.util import *

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
    def run(self, stopping_criteria=default_stopping_criteria, result_=None):
        self.stats = GreedyLearnerStatistics()
        self.result = result_ or result.LearnerResult(self)
        
        scorertype = cond(self.data.has_missingvals, scorer.MissingDataManagedScorer, scorer.ManagedScorer)
        self.scorer = scorertype(self.network, self.data)

        self.result.start_run(self)

        while not stopping_criteria(self.stats):
            self._run_without_restarts(stopping_criteria)
        
        self.result.stop_run()
    
    def _run_without_restarts(self, stopping_criteria):
        self.stats.restarts += 1
        self.scorer.randomize_network()
        
        # reset all stats except iterations and runtime
        self.stats.best_score = self.scorer.score_network()

        # continue learning till the stopping criteria is met (function returns True)
        while not stopping_criteria(self.stats):
            self.stats.iterations += 1

            try:
                self._alter_network_randomly()
            except CannotAlterNetworkException:
                return
            
            curscore = self.scorer.score_network()
            self.result.add_network(self.scorer.network, curscore)

            if curscore < self.stats.best_score:
                # score did not improve, undo network alteration
                self.stats.unimproved_iterations += 1
                self.scorer.restore_network()
            else:
                self.stats.best_score = curscore
                self.stats.unimproved_iterations = 0
 

