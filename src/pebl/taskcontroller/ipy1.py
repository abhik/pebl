"""Classes and functions for running tasks using IPython1"""

from __future__ import with_statement

import os, os.path
import tempfile
import cPickle

from pebl import config, result
from pebl.taskcontroller.base import _BaseSubmittingController, DeferredResult

try:
    import ipython1.kernel.api as ipy1kernel
except:
    ipy1kernel = False

class IPython1DeferredResult(DeferredResult):
    def __init__(self, ipy1_taskcontroller, taskid):
        self.tc = ipy1_taskcontroller
        self.taskid = taskid

    @property
    def result(self):
        if not hasattr(self, '_result'):
            self.ipy1result = self.tc.getTaskResult(self.taskid)

        return self.ipy1result['result']

    @property
    def finished(self):
        rst = self.tc.getTaskResult(self.taskid, block=False)
        if rst:
            self.ipy1result = rst
            return True
        return False

class IPython1Controller(_BaseSubmittingController):
    _params = (
        config.StringParameter(
            'ipython1.controller',
            'IPython1 TaskController (default is 127.0.0.1:10113)',
            default='127.0.0.1:10113'
        )
    )
 
    def __init__(self, tcserver=None):
        """Create a IPython1Controller instance.

        tcserver is the server and port of the Ipython1 TaskController. 
        It should be of the form <ip>:<port>. (default is "127.0.0.1:10113").
        
        """
        
        if not ipy1kernel:
            print "IPython1 not found."
            return None
    
        self.tcserver = tcserver or config.get('ipython1.controller')
        self.tc = ipy1kernel.TaskController(tuple(self.tcserver.split(':')))

    def submit(self, tasks):
        drs = []
        for task in tasks:
            ipy1task = ipy1kernel.Task(
                "from pebl.pebl_script import runtask_picklestr; result = runtask_picklestr(task)",
                resultNames = ['result'],
                setupNS = {'task': cPickle.dumps(task)}
            )
            
            task.ipy1_taskid = self.tc.run(ipy1task)
            drs.append(IPython1DeferredResult(self.tc, task.ipy1_taskid))
        return drs

    def retrieve(self, deferred_results):
        # block/wait for all tasks
        taskids = [dr.taskid for dr in deferred_results]
        self.tc.barrier(taskids)
        return [dr.result for dr in deferred_results]
    

