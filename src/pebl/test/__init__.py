import tempfile, os

location = tempfile.mkdtemp()
def setup():
    os.chdir(location)

def teardown():
    os.system("rm -rf %s" % location)
