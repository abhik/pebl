from pebl import config
from pebl.taskcontroller.base import *

#
# Module Parameteres
#
_pcontrollertype = config.StringParameter(
    'taskcontroller.type',
    'The task controller to use.',
    default = 'serial.SerialController'
)


#TODO:test
def fromconfig():
    tctype = config.get('taskcontroller.type')
    tcmodule,tcclass = tctype.split('.')
    mymod = __import__("pebl.taskcontroller.%s" % tcmodule, fromlist=['pebl.taskcontroller'])
    mytc = getattr(mymod, tcclass)
    return mytc()




