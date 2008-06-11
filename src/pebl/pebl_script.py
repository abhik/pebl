import sys
import os, os.path
import cPickle

# import everything to make sure that all config parameters get registered
from pebl import config, data, network, learner, taskcontroller, result, prior, result, posterior
from pebl.learner import greedy, simanneal, exhaustive
#from pebl.taskcontroller import serial, multiprocess, ec2, xgrid


USAGE = """
Usage: %s <action> [<action parameters>]

Actions
-------
run <configfile>        
    Runs pebl based on params in config file.

runtask <picklefile>    
    Unpickles the file and calls run() on it.
    <picklefile> should be a a pickled learner or task.

viewhtml <resultfile> <outputdir>  
    Creates a html report of the results.
    <resultfile> should be a pickled pebl.result.
    <outputdir> is where the html files will be placed.
    It will be created if it does not exist.

""" % os.path.basename(sys.argv[0])

def usage(msg, exitcode=-1):
    print "Pebl: Python Envinronment for Bayesian Learning"
    print "-----------------------------------------------"
    print "\n==============================================="
    print "ERROR:", msg
    print "===============================================\n"
    print USAGE
    sys.exit(exitcode)

def main():
    """The pebl script.
    
    This is installed by setuptools as /usr/local/bin/pebl.

    """
    
    if len(sys.argv) < 2:
        usage("Please specify the action.")

    if sys.argv[1] in ('run', 'runtask', 'viewhtml'):
        action = eval(sys.argv[1])
        action()
    else:
        usage("Action %s not found." % sys.argv[1])

def run(configfile=None):
    try:
        configfile = configfile or sys.argv[2]
    except:
        usage("Please specify a config file.")

    config.read(configfile)

    numtasks = config.get('learner.numtasks')
    tasks = [learner.fromconfig() for i in xrange(numtasks)]

    controller = taskcontroller.fromconfig()
    controller.start()
    results = controller.run(tasks)
    controller.stop()
    
    result.merge(results).tofile()

def runtask(picklefile=None):
    try:
        picklefile = picklefile or sys.argv[2]
    except:
        usage("Please specify a pickled task file.")

    outfile = os.path.join(os.path.dirname(picklefile), 'result.pebl')
    learntask = cPickle.load(open(picklefile))
    result = learntask.run()
    result.tofile(outfile)

def viewhtml(resultfile=None, outdir=None):
    try:
        resultfile = resultfile or sys.argv[2]
        outdir = outdir or sys.argv[3]
    except:
        usage("Please specify the result file and output directory.")

    cPickle.load(open(resultfile)).tohtml(outdir)

# -----------------------------
if __name__ == '__main__':
    main()

