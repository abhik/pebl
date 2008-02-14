import tempfile
import os, os.path
import inspect
import doctest

# make sure that any files created during running tests are created in a temp
# directory (and later deleted)

location = tempfile.mkdtemp()
def setup():
    os.chdir(location)

def teardown():
    os.system("rm -rf %s" % location)

def testfile(fname):
    """Returns the full path for the specified file in the test directory."""

    return os.path.join(
            os.path.dirname(inspect.getfile(testfile)),
            'testfiles',
            fname
    )

# so nose doesn't think it's a test
testfile.__test__ = False

def run(module=None):
    failed,total = doctest.testmod(module)
    
    print "%d of %d failed." % (failed,total) 

