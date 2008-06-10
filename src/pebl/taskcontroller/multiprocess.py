"""Module providing a taskcontroller than runs tasks over multiple processes."""

import os, os.path
import cPickle
import thread, time
import shutil 
import tempfile
from copy import copy

from pebl import config, result
from pebl.taskcontroller.base import _BaseController

PEBL = "pebl"

class MultiProcessController(_BaseController):
    #
    # Parameters
    # 
    _params = (
            config.IntParameter(
            'multiprocess.poolsize',
            'Number of processes to run concurrently (0 means no limit)',
            default=0
        )
    )
        
    def __init__(self, poolsize=None):
        """Creates a task controller that runs taks on multiple processes.

        This task controller uses a pool of processes rather than spawning all
        processes concurrently. poolsize is the size of this pool and by
        default it is big enough to run all processes concurrently.

        """
        self.poolsize = poolsize or config.get('multiprocess.poolsize')

    def run(self, tasks):
        """Run tasks by creating multiple processes.

        If poolsize was specified when creating this controller, additional
        tasks will be queued.

        """
        tasks = copy(tasks) # because we do tasks.pop() below..
        numtasks = len(tasks)
        poolsize = self.poolsize or numtasks
        running = {}
        done = []
        opjoin = os.path.join

        while len(done) < numtasks:
            # submit tasks (if below poolsize and tasks remain)
            for i in xrange(min(poolsize-len(running), len(tasks))):
                task = tasks.pop()
                task.cwd = tempfile.mkdtemp()
                cPickle.dump(task, open(opjoin(task.cwd, 'task.pebl'), 'w'))
                pid = os.spawnlp(os.P_NOWAIT, PEBL, PEBL, "runtask", 
                                 opjoin(task.cwd, "task.pebl"))
                running[pid] = task
            
            # wait for any child process to finish
            pid,status = os.wait() 
            done.append(running.pop(pid, None))

        results = [result.fromfile(opjoin(t.cwd, 'result.pebl')) for t in done]
        for t in done:
            shutil.rmtree(t.cwd)

        return results
