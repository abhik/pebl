from pebl import network, distributions, result
from pebl.util import cond
import scorer
from __init__ import *
from math import exp


class SALearnerStatistics:
    def __init__(self, starting_temp, delta_temp, max_iterations_at_temp):
        self.temp = starting_temp
        self.iterations_at_temp = 0
        self.max_iterations_at_temp = max_iterations_at_temp
        self.delta_temp = delta_temp

        self.iterations = 0
        self.best_score = 0
        self.current_score = 0

    def update(self):
        self.iterations += 1
        self.iterations_at_temp += 1

        if self.iterations_at_temp >= self.max_iterations_at_temp:
            self.temp *= self.delta_temp
            self.iterations_at_temp = 0


class SimulatedAnnealingLearner(Learner):
    def run(self, result_=None, starting_temp=100, delta_temp=.5, max_iterations_at_temp=100):
        self.stats = SALearnerStatistics(starting_temp, delta_temp, max_iterations_at_temp)
        self.result =  result_ or result.LearnerResult(self)
        
        scorertype = cond(self.data.has_missingvals, scorer.MissingDataManagedScorer, scorer.ManagedScorer)
        self.scorer = scorertype(self.network, self.data)

        self.result.start_run(self)

        self.scorer.randomize_network()
        curscore = self.scorer.score_network()
        
        # temperature decays exponentially, so we'll never get to 0. So, we continue until temp < 1
        while self.stats.temp >= 1:
            try:
                self._alter_network_randomly()
            except CannotAlterNetworkException:
                return

            newscore = self.scorer.score_network()
            self.result.add_network(self.scorer.network, newscore)

            if self.accept(newscore):
                # set current score
                self.stats.current_score = newscore
                if self.stats.current_score > self.stats.best_score:
                    self.stats.best_score = self.stats.current_score
            else:
                # undo network alteration
                self.scorer.restore_network()

            # temp not updated EVERY iteration. just whenever criteria met.
            self.stats.update() 

        self.result.stop_run()

    def accept(self, newscore):
        oldscore = self.stats.current_score

        if newscore >= oldscore:
            return True
        elif random.random() < exp((newscore - oldscore)/self.stats.temp):
            return True
        else:
            return False

