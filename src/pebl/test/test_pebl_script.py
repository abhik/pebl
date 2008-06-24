from __future__ import with_statement
import textwrap 
import tempfile
import os.path
import shutil

from pebl import pebl_script
from pebl.test import testfile

class TestHtmlReport:
    def setup(self):
        self.tempdir = tempfile.mkdtemp()
        self.outdir = os.path.join(self.tempdir, 'result')

        htmlreport_config = textwrap.dedent("""
        [data]
        filename = %s

        [result]
        format = html
        outdir = %s
        """ % (testfile("testdata12.txt"), self.outdir))
        
        configfile = os.path.join(self.tempdir, "config.txt")
        with file(configfile, 'w') as f:
            f.write(htmlreport_config)

    def teardown(self):
        shutil.rmtree(self.tempdir)

    def test_htmlreport(self):
        pebl_script.run(os.path.join(self.tempdir, 'config.txt'))
        os.path.exists(os.path.join(self.outdir, 'index.html'))


        
