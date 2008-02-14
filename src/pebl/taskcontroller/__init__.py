from __future__ import with_statement
from pebl import config
from pebl.taskcontroller.base import *
from pebl.taskcontroller.serial import SerialController
from pebl.taskcontroller.multiprocess import MultiProcessController
from pebl.taskcontroller.xgrid import XgridController

#
# controller name --> class map
#
_controllers = {
    'serial': SerialController,
    'multiprocess': MultiProcessController,
    'xgrid': XgridController
}


#
# Module Parameteres
#
_pcontrollertype = config.StringParameter(
    'taskcontroller.type',
    'The task controller to use.',
    config.oneof(*_controllers.keys()),
    default = 'serial'
)


#TODO:test
def fromconfig():
    controllertype = _controllers.get(config.get('taskcontroller.type'))
    return controllertype()




