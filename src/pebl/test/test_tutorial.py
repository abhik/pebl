"""tests all the code included in the pebl tutorial"""

from __future__ import with_statement 
import tempfile, shutil, os.path
import textwrap

from pebl import data, pebl_script
from pebl.learner import greedy, simanneal
from pebl.test import testfile

class TestTutorial:
    def setup(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown(self):
        shutil.rmtree(self.tmpdir)

    def test_example1(self):
        outdir = os.path.join(self.tmpdir, "example1-result")

        dataset = data.fromfile(testfile("pebl-tutorial-data1.txt"))
        dataset.discretize()
        learner = greedy.GreedyLearner(dataset)
        ex1result = learner.run()
        ex1result.tohtml(outdir)

        assert os.path.exists(os.path.join(outdir, 'index.html'))

    def test_example1_configfile(self):
        configfile = os.path.join(self.tmpdir, 'config1.txt')
        outdir = os.path.join(self.tmpdir, "example1-result-2")

        configstr = textwrap.dedent("""
        [data]
        filename = %s
        discretize = 3

        [learner]
        type = greedy.GreedyLearner

        [result]
        format = html
        outdir = %s
        """ % (testfile("pebl-tutorial-data1.txt"), outdir))
        
        with file(configfile, 'w') as f:
            f.write(configstr)

        pebl_script.run(configfile)
        assert os.path.exists(os.path.join(outdir, 'data', 'result.data.js'))

