import os, sys, signal, os.path
import subprocess
import time

from ipython1.kernel.scripts import ipcluster 
from ipython1.kernel import task, controllerservice as cs, engineservice as es

from pebl import data, result
from pebl.learner import greedy
from pebl.taskcontroller import serial, multiprocess, ipy1
from pebl.test import testfile

# NOTE: The EC2 task controller is not tested automatically because:
#   1. it requires authentication credential that we can't put in svn
#   2. don't want to spend $$ everytime we run pebl's unittest.
# So, it's in pebl/test.manual/test_ec2.py

class TestSerialTC:
    tctype = serial.SerialController
    args = ()

    def setUp(self):
        d = data.fromfile(testfile("testdata5.txt"))
        d.discretize()
        
        self.tc = self.tctype(*self.args)
        self.tasks = [greedy.GreedyLearner(d, max_iterations=100) for i in xrange(6)]

    def test_tc(self):
        results = self.tc.run(self.tasks)
        results = result.merge(results)
        assert isinstance(results, result.LearnerResult)

class TestMultiProcessTC(TestSerialTC):
    tctype = multiprocess.MultiProcessController
    args = (2,)

class TestIPython1TC:
    # I've tried any ways of creating and terminating the cluster but the
    # terminating always fails.. So, for now, you have to kill the cluster
    # manually.
    
    def setUp(self):
        d = data.fromfile(testfile("testdata5.txt"))
        d.discretize()

        self.proc = subprocess.Popen("ipcluster -n 2 </dev/null 1>&0 2>&0", shell=True)
        time.sleep(5)
    
    def tearDown(self):
        os.kill(self.proc.pid, signal.SIGINT)
        time.sleep(5)

    def test_tc(self):
        d = data.fromfile(testfile("testdata5.txt"))
        d.discretize()
        tasks = [greedy.GreedyLearner(d) for x in range(5)]
        tc = ipy1.IPython1Controller("127.0.0.1:10113")
        results = tc.run(tasks)
        results = result.merge(results)
        assert isinstance(results, result.LearnerResult)
