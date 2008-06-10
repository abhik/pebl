import sys, os, os.path
from functools import partial
import shutil

import numpy as N

from pebl import network, config, evaluator, data, prior
from pebl.learner.base import Learner


#TODO: test
class CustomLearner(Learner):
    def __init__(self, data_=None, prior_=None, learnerurl=':', **kw):
        """Create a CustomLearner wrapper.

        If you don't use a TaskController, you can simply create a custom
        learner (as a Learner subclass) and run it.  With a TaskController,
        however, the learner might run on a different machine and so its code
        needs to be copied over to any worker machine(s).  This is what
        CustomLearner does.

        learnerurl is your custom learner class specified as "<file>:<class>"
        (for example, "/Users/shahad/mycode.py:SuperLearner").

        Example::

            dataset = data.fromfile("data.txt")
            tc = taskcontroller.XgridController()
            mylearner = CustomLearner(
                dataset, 
                learnerurl="/Users/shahad/mycode.py:SuperLearner"
            )
            
            # learner will run on the Xgrid (where mycode.py doesn't exist)
            results = tc.run([mylearner]) 

        """

        # save info so custom learner can be recreated at run (possibly on a
        # different machine)
        self.learner_filename, self.learner_class = learnerurl.split(':')
        self.learner_source = open(self.learner_filename).read()
        self.data = data_
        self.prior = prior_
        self.kw = kw

    def run(self):
        # recreate the custom learner
        tempdir = tempfile.mkdtemp()
        tempfile = partial(os.path.join, tempdir)
        open(tempfile(self.learner_filename), 'w').write(self.learner_source)

        sys.path.insert(0, tempdir)
        modname = os.path.basename(self.learner_filename).split('.')[0]
        mod = __import__(modname, fromlist=['.'])
        custlearner = getattr(mod, self.learner_class)

        # run the custom learner
        custlearner(
            self.data_ or data.fromconfig(), 
            self.prior_ or prior.fromconfig(),
            **self.kw
        ).run()

        self.result = custlearner.result

        # cleanup
        sys.path.remove(tempdir)
        shutil.rmtree(tempdir)

        return self.result

