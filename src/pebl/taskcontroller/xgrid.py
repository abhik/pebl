import time
import os.path
import shutil 
import tempfile

try:
    import xg
    XG_LOADED = True
except:
    XG_LOADED = False
    
from pebl import config, result
from pebl.taskcontroller.base import _BaseController, DeferredResult

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

        print rst
        return rst
 
    @property
    def finished(self):
        print self.job, self.job.info(update=1)
        return self.job.info(update=1).get('jobStatus') in ('Finished',)


class XgridController(_BaseController):

    #
    # Parameters
    #
    _pcontroller = config.StringParameter(
        'xgrid.controller',
        'Hostname or IP of the Xgrid controller.',
        default=''
    )

    _ppassword = config.StringParameter(
        'xgrid.password',
        'Password for the Xgrid controller.',
        default=''
    )

    _pgrid = config.StringParameter(
        'xgrid.grid',
        'Id of the grid to use at the Xgrid controller.',
        default='0'
    )

    _ppoll = config.FloatParameter(
        'xgrid.pollinterval',
        'Time (in secs) to wait between polling the Xgrid controller.',
        default=60.0
    )

    _ppeblpath = config.StringParameter(
        'xgrid.peblpath',
        'Full path to the pebl script on Xgrid agents',
        default='pebl'
    )

    def __init__(self, controller=None, password=None, grid=None,
                 pollinterval=None, peblpath=None): 
        
        self.controller = controller or config.get('xgrid.controller')
        self.password = password or config.get('xgrid.password')
        self.gridnum = grid or config.get('xgrid.grid')
        self.pollinterval = pollinterval or config.get('xgrid.pollinterval')
        self.peblpath = peblpath or config.get('xgrid.peblpath')

    @property
    def _grid(self):
        if XG_LOADED:
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
            task._prepare_config(workingdir_is_tmp=False)
            task.job = grid.submit(self.peblpath, 'config.txt', indir=task.cwd)
            print "jobid:", task.job.jobID
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

    def run(self, tasks):
        return self.retrieve(self.submit(tasks))

