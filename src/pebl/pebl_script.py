import sys
import os, os.path
import cPickle

# import everything to make sure that all config parameters get registered
from pebl import config, data, network, learner, taskcontroller, result, prior, result, posterior
from pebl.learner import greedy, simanneal, exhaustive
#from pebl.taskcontroller import serial, multiprocess, ec2, xgrid

_pcwd = config.StringParameter(
    'pebl.workingdir',
    'Working directory for pebl.',
    default='.'
)

def main():
    """The pebl script.
    
    This is installed by setuptools as /usr/local/bin/pebl.

    """

    if len(sys.argv) < 2:
        print "Usage: %s configfile" % os.path.basename(sys.argv[0])
        sys.exit()

    results = runpebl(sys.argv[1])

    if all(isinstance(r, result.LearnerResult) for r in results):
        finalresult = result.merge(results)
        finalresult.tofile()
    else:
        cPickle.dump(results, open(config.get('result.filename'), 'w'))

    
def runpebl(configfile):
    config.read(configfile)
    os.chdir(config.get('pebl.workingdir'))

    numtasks = config.get('learner.numtasks')
    tasks = [learner.fromconfig() for i in xrange(numtasks)]
    controller = taskcontroller.fromconfig()

    controller.start()
    results = controller.run(tasks)
    controller.stop()

    return results

# -----------------------------
if __name__ == '__main__':
    main()

