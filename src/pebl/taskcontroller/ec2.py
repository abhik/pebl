"""Classes and functions for running tasks on Amazon's EC2"""

import time
import os.path
import shutil 
import tempfile
import sys

from pebl import config, result
from pebl.taskcontroller.ipy1 import IPython1Controller, IPython1DeferredResult
from pebl.taskcontroller import ec2ipy1

class EC2DeferredResult(IPython1DeferredResult):
    pass

class EC2Controller(IPython1Controller):
    _params = (
        config.StringParameter(
            'ec2.config',
            'EC2 config file',
            default=''
        ),
        config.IntParameter(
            'ec2.min_count',
            'Minimum number of EC2 instances to create (default=1).',
            default=1
        ),
        config.IntParameter(
            'ec2.max_count',
            """Maximum number of EC2 instances to create 
            (default=0 means the same number as ec2.min_count).""",
            default=0
        )
    )

    def __init__(self, **options):
        config.setparams(self, options)
        self.ec2 = ec2ipy1.EC2Cluster(self.config)
        self.start()

    def __del__(self):
        self.stop()

    def start(self):
        self.ec2.create_instances(self.min_count, self.max_count)

        print "Updating pebl on worker nodes"
        self.ec2.remote_all("cd /usr/local/src/pebl; svn update; python setup.py install")

        self.ec2.start_ipython1(engine_on_controller=True)
        self.ipy1taskcontroller = IPython1Controller(self.ec2.task_controller_url) 

    def stop(self):
        self.ec2.terminate_instances()

    def submit(self, tasks):
        return self.ipy1taskcontroller.submit(tasks)

    def retrieve(self, deferred_results):
        return self.ipy1taskcontroller.retrieve(deferred_results)

    def run(self, tasks):
        return self.ipy1taskcontroller.run(tasks)

