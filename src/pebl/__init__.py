# import everything to make sure that all parameters get registered
import sys
import os
import cPickle

from pebl import config
from pebl import data, network, learner, taskcontroller, result, prior, result, posterior
from pebl.learner import greedy, simanneal, exhaustive


_pcwd = config.StringParameter(
    'pebl.workingdir',
    'Working directory for pebl.',
    default='.'
)

def main():
    """The pebl script."""

    if len(sys.argv) < 2:
        print "Usage: %s configfile" % sys.argv[0]
        sys.exit()
    
    config.read(sys.argv[1])
    os.chdir(config.get('pebl.workingdir'))


    numtasks = config.get('learner.numtasks')
    tasks = [learner.fromconfig() for i in xrange(numtasks)]
    controller = taskcontroller.fromconfig()

    controller.start()
    results = controller.run(tasks)
    controller.stop()

    if all(isinstance(r, result.LearnerResult) for r in results):
        finalresult = result.merge(results)
        finalresult.tofile()
    else:
        cPickle.dump(results, open(config.get('result.filename'), 'w'))



