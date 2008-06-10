import time
import os.path
import shutil 
import tempfile

try:
    import xg
except:
    xg = False
    
from pebl import config, result
from pebl.taskcontroller.base import _BaseSubmittingController, DeferredResult

class XgridDeferredResult(DeferredResult):
    def __init__(self, grid, task):
        self.grid = grid
        self.job = task.job

    @property
    def result(self):
        tmpdir = tempfile.mkdtemp('pebl')
        self.job.results(
            stdout = os.path.join(tmpdir, 'stdout'),
            stderr = os.path.join(tmpdir, 'stderr'),
            outdir = tmpdir
        )
        self.job.delete()
        rst = result.fromfile(os.path.join(tmpdir,'result.pebl'))
        shutil.rmtree(tmpdir)  

        return rst
 
    @property
    def finished(self):
        print self.job, self.job.info(update=1)
        return self.job.info(update=1).get('jobStatus') in ('Finished',)


class XgridController(_BaseSubmittingController):
    #
    # Parameters
    #
    _params = (
        config.StringParameter(
            'xgrid.controller',
            'Hostname or IP of the Xgrid controller.',
            default=''
        ),
        config.StringParameter(
            'xgrid.password',
            'Password for the Xgrid controller.',
            default=''
        ),
        config.StringParameter(
            'xgrid.grid',
            'Id of the grid to use at the Xgrid controller.',
            default='0'
        ),
        config.FloatParameter(
            'xgrid.pollinterval',
            'Time (in secs) to wait between polling the Xgrid controller.',
            default=60.0
        ),
        config.StringParameter(
            'xgrid.peblpath',
            'Full path to the pebl script on Xgrid agents.',
            default='pebl'
        )
    )

    def __init__(self, **options):
        """Create a XGridController.

        Any config param for 'xgrid' can be passed in via options.
        Use just the option part of the parameter name.
        
        """
        config.setparams(self, options)

    @property
    def _grid(self):
        if xg:
            cn = xg.Connection(self.controller, self.password)
            ct = xg.Controller(cn)
            return ct.grid(self.gridnum)

        return None

    #
    # Public interface
    #
    def submit(self, tasks):
        grid = self._grid

        drs = []
        for task in tasks:
            task.cwd = tempfile.mkdtemp()
            cPickle.dump(task, open(os.path.join(task.cwd, 'task.pebl'), 'w'))
            task.job = grid.submit(self.peblpath, 'runtask task.pebl', 
                                   indir=task.cwd)
            drs.append(XgridDeferredResult(grid, task))
        return drs
   
    def retrieve(self, deferred_results):
        drs = deferred_results
        print drs

        # poll for job results
        # i'd rather select() or wait() but xgrid doesn't offer that via the
        # xgrid command line app
        done = []
        while drs:
            for i,dr in enumerate(drs):
                if dr.finished:
                    done.append(drs.pop(i))
                    break  # modified drs, so break and re-iterate
            else:
                time.sleep(self.pollinterval)

        return [dr.result for dr in done] 

