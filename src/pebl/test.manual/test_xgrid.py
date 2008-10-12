import sys
from pebl import data, result, config
from pebl.learner import greedy
from pebl.taskcontroller import xgrid
from pebl.test import testfile

help = """Test the Xgrid TaskController.

USAGE: test_xgrid.py configfile

You need to provide the configfile for use with XGridController.

###############################################################################
    WARNING for pebl devs: 
        Do NOT put your configfile under svn. 
        It contains sensitve information.
###############################################################################
"""

if len(sys.argv) < 2:
    print help
    sys.exit(1)

config.read(sys.argv[1])
d = data.fromfile(testfile("testdata5.txt"))
d.discretize()

tc = xgrid.XgridController()
results = tc.run([greedy.GreedyLearner(d, max_time=10) for i in xrange(10)])
results = result.merge(results)

print results
print [r.host for r in results.runs]
