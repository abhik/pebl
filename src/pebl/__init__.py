# import sub-modules so they're in the namespace and available to
# tab-completion in ipython
import config, cpd, data, discretizer, evaluator, network, posterior, prior, \
       result, util 

import learner.base, learner.greedy, learner.custom, learner.simanneal, \
       learner.exhaustive 

# BUT, don't import the taskcontroller sub-modules because some of them are
# optional features with extra dependencies.
