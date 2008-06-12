import sys
from pebl import data, result
from pebl.learner import greedy
from pebl.taskcontroller import ec2
from pebl.test import testfile

help = """Test the EC2 TaskController.

USAGE: test_ec2.py configfile

You need to provide the configfile for use with EC2Controller.

###############################################################################
    WARNING for pebl devs: 
        Do NOT put your configfile under svn. 
        It contains sensitve information.
###############################################################################
"""

if len(sys.argv) < 2:
    print help
    sys.exit(1)

d = data.fromfile(testfile("testdata5.txt"))
d.discretize()

tc = ec2.EC2Controller(config=sys.argv[1], min_count=3)
tc.start()
results = tc.run([greedy.GreedyLearner(d, max_time=10) for i in xrange(10)])
results = result.merge(results)
tc.stop()

print results
print [r.host for r in results.runs]
