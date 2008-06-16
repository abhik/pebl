from pebl import data, result
from pebl.learner import greedy
from pebl.taskcontroller import serial, multiprocess
from pebl.test import testfile

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

class TestMultiProcessTC(TestSerialTC):
    tctype = multiprocess.MultiProcessController
    args = (2,)


