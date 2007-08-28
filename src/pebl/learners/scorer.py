from pebl.util import *
from numpy import *
from pebl import data, distributions

random.seed()

class BasicScorer(object):
    def __init__(self, network_, pebldata, prior_=None):
        self.network = network_
        self.data = pebldata
        self.prior = prior_
        self.cached_localscores = {}

    def _globalscore_from_localscores(self, localscores):
        return sum(localscores)
    
    def _create_distribution(self, node):
        parents = self.network.edges.parents(node)
        datasubset = self.data.subset(
            variables = [node]+parents, 
            samples = self.data.noninterventions_for_variable(node),
            ignore_names = True
        )

        # TODO: when we suport more than one distribution, we'll need a way to specify which type to use
        #       maybe some config parameter..
        return distributions.MultinomialDistribution(datasubset)

    def _score_node(self, node):
        index = self.index(node)
        score = self.cached_localscores.get(index, None)

        if not score:
            score = self._create_distribution(node).loglikelihood()
            self.cached_localscores[index] = score

        return score
    
    def index(self, node):
        return tuple([node] + self.network.edges.parents(node))

    def score_network(self):
        localscores = (self._score_node(node) for node in xrange(self.data.numvariables))
        return globalscore_from_localscores(localscores)

class ManagedScorer(BasicScorer):
    def __init__(self, network_, pebldata, prior_=None):
        super(ManagedScorer, self).__init__(network_, pebldata, prior_)
        self.localscores = zeros((self.data.numvariables), dtype=float)
        self.dirtynodes = [i for i in xrange(self.data.numvariables)]
        self.last_alteration = ()
        self.cached_localscores = {}
        self.saved_localscores = None
        self.score = None

    def _backup_state(self):
        self.saved_localscores = self.localscores[self.dirtynodes].copy()
        self.saved_localscores_indices = self.dirtynodes
        self.saved_score = self.score

    def _restore_state(self):
        self.localscores[self.saved_localscores_indices] = self.saved_localscores
        self.score = self.saved_score

    def alter_network(self, add=[], remove=[]):
        """Alter the network while retaining the ability to *quickly* undo the changes."""

        add = ensure_list(add)
        remove = ensure_list(remove)
        
        for edge in add: 
            self.network.edges.add(edge)    
        for edge in remove: 
            self.network.edges.remove(edge)

        if not self.network.is_acyclic():
            for edge in add: 
                self.network.edges.remove(edge)
            for edge in remove: 
                self.network.edges.add(edge)
            return False
        
        self.last_alteration = (add, remove)    
        self._backup_state()
        
        # Edge src-->dest was added or removed. either way, dest's parentset changed and is thus dirty.
        self.dirtynodes.extend(unzip(add+remove, 1))
        return True

    def restore_network(self):
        """Restore the network to the state before the last call to alter_network()."""

        added, removed = self.last_alteration
        self._restore_state()
        self.dirtynodes = []

        for edge in removed: 
            self.network.edges.add(edge)
        for edge in added: 
            self.network.edges.remove(edge)

    def score_network(self):
        # no nodes are dirty, so just return last score.
        if len(self.dirtynodes) == 0:
            return self.score

        # update localscore for dirtynodes, then calculate globalscore.
        for node in unique(self.dirtynodes):
            self.localscores[node] = self._score_node(node)
        
        self.dirtynodes = []
        self.score = self._globalscore_from_localscores(self.localscores)
        return self.score

    def randomize_network(self):
        self.network.randomize()
        self.dirtynodes = [i for i in xrange(self.data.numvariables)]
    
    def set_network(self, net):
        self.network = net
        self.dirtynodes = [i for i in xrange(self.data.numvariables)]


class GibbsSamplerState(object):
    """Represents the state of the Gibbs sampler.

    This state object can be used to resume the Gibbs sampler from a particaular point.
    Note that the state does not include the network or data and it's upto the caller to ensure
    that the Gibbs sampler is resumed with the same network and data.

    The following variabels are saved:
        - number of sampled scores (numscores)
        - average score (avgscore)
        - most recent value assignments for missing values (assignedvals)

    """

    def __init__(self, avgscore, numscores, assignedvals):
        autoassign(self, locals())

class MissingDataManagedScorer(ManagedScorer):
    """WITH MISSING DATA."""
    gibbs_burnin = 10

    def _score_network(self):
        # update localscore for data_dirtynodes, then calculate globalscore.
        for node in unique(self.data_dirtynodes):
            self.localscores[node] = self._score_node(node)

        self.data_dirtynodes = []
        return self._globalscore_from_localscores(self.localscores)

    def _backup_state(self):
        self.saved_score = self.score

    def _restore_state(self):
        self.score = self.saved_score
    
    def _score_node(self, node):
        if not self.sflist[node]:
            self.sflist[node] = self._create_distribution(node)
        
        return self.sflist[node].loglikelihood()

    def _alter_data(self, row, col, value, interventions):
        oldrow = self.data[row].copy()
        self.data[row][col] = value

        # A column in data corresponds to a node in network.
        altered_node = col
        affected_nodes = [altered_node] + \
                         self.network.edges.parents(altered_node) + \
                         self.network.edges.children(altered_node)
        self.data_dirtynodes.extend(affected_nodes)

        for node in unique(affected_nodes):
            datacols = [node] + self.network.edges.parents(node)
            if node not in interventions[row]:
                self.sflist[node].remove_data(oldrow[datacols])
                self.sflist[node].add_data(self.data[row][datacols])

    def _score_after_altering_data(self, row, col, value, interventions):
        self._alter_data(row, col, value, interventions)
        return self._score_network()

    def score_network(self, stopping_criteria=None, gibbs_state=None, save_state=False):
        # rescore if ANY nodes are dirty.
        if len(self.dirtynodes) == 0:
            return self.score

        # network was altered.. so reset sflist and data_dirtynodes
        self.sflist = [None for i in xrange(self.data.numvariables)]
        self.data_dirtynodes = range(self.data.numvariables)

        # create some useful lists and vars
        interventions = [self.data.interventions_for_sample(s) for s in xrange(self.data.numsamples)]
        missingvals = self.data.indices_of_missingvals
        num_missingvals = len(missingvals)
        arities = self.data.arities
        chosenscores = []

        # set missing values using last assigned values from previous gibbs run or random values based on node arity
        if gibbs_state:
            assignedvals = gibbs_state.assignedvals
        else:
            assignedvals = (random.random_integers(0, arities[col]-1, 1) for row,col in missingvals)
        
        for (row,col),val in zip(missingvals, assignedvals):
            self.data[row][col] = val

        # score to initialize sflist, etc.
        self._score_network()

        # default stopping criteria is to sample for N^2 iterations (N == number of missing vals)
        stopping_criteria = stopping_criteria or (lambda scores,iterations,N: iterations >= num_missingvals**2)

        # === Gibbs Sampling === 
        # For each missing value:
        #    1) score net with each possible value (based on node's arity)
        #    2) using a probability wheel, sample a value from the possible values (and set it in the dataset)
        iterations = 0
        while not stopping_criteria(chosenscores, iterations, num_missingvals):
            for row,col in missingvals:
                scores = [self._score_after_altering_data(row, col, val, interventions) for val in xrange(arities[col])]
                chosenval = logscale_probwheel(scores)
                self._alter_data(row, col, chosenval, interventions)
                chosenscores.append(scores[chosenval])
            
            iterations += num_missingvals

        chosenscores = array(chosenscores)
        
        # discard the burnin period scores and average the rest
        burnin_period = self.gibbs_burnin * num_missingvals
        if gibbs_state:
            # resuming from a previous gibbs run. so, no burnin required.. so, use all scores.
            scoresum = sum(chosenscores) + (gibbs_state.avgscore * gibbs_state.numscores)
            numscores = len(chosenscores) + gibbs_state.numscores
        elif len(chosenscores) > burnin_period:
            # not resuming from previous gibbs run. so remove scores from burnin period.
            nonburn_scores = chosenscores[burnin_period:]
            scoresum = sum(nonburn_scores)
            numscores = len(nonburn_scores)
        else:
            # this occurs when gibbs iterations were less than burnin period. so use last score.
            scoresum = chosenscores[-1]
            numscores = 1
        
        # set self.score and self.sampled_scores
        self.sampled_scores = chosenscores
        self.score = scoresum/numscores

        # save state of gibbs sampler?
        # unzip transforms [(a,b), (c,d), (e,f)] into [[a,c,e], [b,d,f])
        # So unzip(missingvals) returns missing value indices as a list of rows and list of columns
        # self.data[[row1, row2], [col1, col2]] returns data[row1][col1] and data[row2][col2] 
        if save_state:
            self.gibbs_state = GibbsSamplerState(avgscore=self.score, numscores=numscores, assignedvals=self.data[unzip(missingvals)].tolist())
        
        return self.score

defaultType = ManagedScorer
