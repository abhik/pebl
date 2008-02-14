import time
import os.path
import shutil 
import tempfile
import xg

from pebl import config, result
from pebl.taskcontroller.base import _BaseController, DeferredResult

class EC2Controller(_BaseController):
    _pcontroller = config.StringParameter(
        'ec2.config',
        'EC2 config file',
        default=''
    )
 
    def __init__(self):
        self.ec2 = ec2ipy1.EC2Cluster(config.get('ec2.config')) 
        ec2.create_cluster(config.get('learner.numtasks')+1)
        self.rc = kernel.RemoteController(kernel.defaultRemoteController)
        self.tc = kernel.TaskController(kernel.defaultTaskController)
    
        
