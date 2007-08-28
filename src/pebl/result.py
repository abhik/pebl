from posterior import Posterior
import time
import socket
from util import flatten
from copy import deepcopy


class LearnerRun:
    def __init__(self, learner):
        self.learner_class = learner.__class__.__name__
        self.starttime = time.time()
        self.stoptime = None
        self.hostname = socket.gethostname()

        self.edgelists = []
        self.scores = []

    def stop(self):
        self.stoptime = time.time()


class LearnerResult:
    def __init__(self, learner_):
        self.data = learner_.data
        self.nodes = learner_.network.nodes
        self.runs = []
        self.current_run = None

    def start_run(self, learner):
        # if learner didn't stop last run (could happen if: threw uncaught exception during run)
        if self.current_run:
            self.stop_run()

        self.runs.append(LearnerRun(learner))
        self.current_run = self.runs[-1]

    def stop_run(self):
        self.current_run.stop()
        self.current_run = None
    
    def add_network(self, network, score):
        self.current_run.edgelists.append(deepcopy(network.edges))
        self.current_run.scores.append(score)
    
    def merge(self, other):
        self.runs.extend(other.runs)

    @property
    def posterior(self):
        unique_edgelists = []
        unique_scores = []

        for run in self.runs:
            for edgelist, score in zip(run.edgelists, run.scores):
                if (score not in unique_scores) or (edgelist not in unique_edgelists):
                    unique_scores.append(score)
                    unique_edgelists.append(edgelist)

        return Posterior(self.nodes, [el.adjacency_matrix for el in unique_edgelists], unique_scores)

