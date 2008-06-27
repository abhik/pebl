from __future__ import with_statement
import sys, os, os.path
import tempfile
from functools import partial
import shutil
import cPickle

import numpy as N

from pebl import network, config, evaluator, data, prior
from pebl.learner.base import Learner


#TODO: test
class CustomLearner(Learner):
    def __init__(self, data_, prior_=None, learnerurl=':', **kw):
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
        self.learner_filepath, self.learner_class = learnerurl.split(':')
        self.learner_filename = os.path.basename(self.learner_filepath)
        self.learner_source = open(self.learner_filepath).read()
        self.data = data_
        self.prior = prior_
        self.kw = kw

    def run(self):
        # re-create the custom learner
        tempdir = tempfile.mkdtemp()
        with file(os.path.join(tempdir, self.learner_filename), 'w') as f:
            f.write(self.learner_source)
        
        sys.path.insert(0, tempdir)
        modname = self.learner_filename.split('.')[0]
        mod = __import__(modname, fromlist=['*'])
        
        reload(mod) # to load the latest if an older version exists
        custlearner = getattr(mod, self.learner_class)

        # run the custom learner
        clearn = custlearner(
            self.data or data.fromconfig(), 
            self.prior or prior.fromconfig(),
            **self.kw
        )
        self.result = clearn.run()
        
        # cleanup
        sys.path.remove(tempdir)
        shutil.rmtree(tempdir)

        return self.result

class CustomResult:
    def __init__(self, **kw):
        for k,v in kw.iteritems():
            setattr(self, k, v)

    def tofile(self, filename=None):
        filename = filename or config.get('result.filename')
        with open(filename, 'w') as fp:
            cPickle.dump(self, fp)
 
