Installation
=============

Unfortunatly, installing pebl is not a one-stop process although it should take
no longer than a few minutes. If you experience any problems, please contact me
at abhikshah@gmail.com.

Pebl is known to run on Linux and Mac OSX and should also run on Windows and
any platform that supports Python 2.5 and numpy. Pebl depends on the following
packages:

 * Numpy: tested with version 1.0.4 but should work with other recent versions
 * Pydot: tested with version 1.0.2
 * Matplotlib (optional): tested with version 0.91.2 but should work with other
   recent versions
 * Graphviz (optional): any recent version of dot and neato 
 * IPython1 (optional): curently, require r2815 from svn trunk
 * boto (optional): any recent version


Install Python 2.5
-------------------

Check what version of Python you have with::

    python --version

You can download Python 2.5 from http://python.org/download

.. note:: Pebl requires Python 2.5 or greater and will not run under earlier versions.


Install easy_install
--------------------

easy_install lets you install python packages and their requirements in one
easy step. Unfortunately, easy_install is not distributed with python and needs
to be installed separately.

1. Download ez_setup.py from http://peak.telecommunity.com/dist/ez_setup.py
2. Run :command:`python ez_setup.py` to install easy_install

Run :command:`easy_install --help` to make sure that it is in your path. On
unix-type systems, it is usually installed in /usr/bin/ and on Windows in
C:\\Python2.5\\Scripts\\


Install Numpy
-------------

Numpy can be tricky to install because it require C and Fortran compilers and
several libraries. You can try installing it from source using easy_install::

    easy_install numpy

If that doesn't work or if you'd rather install using a binary package, consult
http://www.scipy.org/Download.

Install Pebl
------------

You can now install (or upgrade) pebl and it's required dependencies using
easy_install::

    easy_install pebl

.. note:: The current version of Pebl is 0.9.10.

If you have downloaded the source code for Pebl (or installing pebl from svn),
you can run :command:`sudo python setup.py install` from pebl's root directory
instead.

Testing Pebl Installation
-------------------------

To test pebl installation, you can run the automated unit tests by first install nose::

    easy_install nose

and then running nose from the command line, in any directory::

    nosetests -v pebl.test

If you haven't installed all the optional dependencies, certain tests will fail
but the name of the tests should make it clear whether it's a normal feature or
an optional one.


Installing optional dependencies
---------------------------------

Certain features of pebl require additional dependencies. You only need to
install these if you need the optional features. Without the optional features,
you can load data, learn networks and output networks in dot format, although
not as an image. If installing pebl on a cluster, the optional features are
only necessary on the controller or the machine used  interactively by the
user.

For creating HTML reports of Pebl results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pebl uses Graphviz to visualize networks and matplotlib for plotting. If using
Pebl on a cluster, these don't need to be installed on the worker nodes.

1. Install Graphviz from http://www.graphviz.org/Download.php
2. Install matplotlib from http://matplotlib.sourceforge.net/installing.html

Finally, install simplejson using easy_install::

    easy_install simplejson

simplejson sometimes fails to install on Windows. In that case, you can use a
binary package::

    easy_install http://pebl-project.googlecode.com/files/simplejson-1.7.3-py2.5-win32.egg

To test the html-report feature, run::

    nosetests -v pebl.test.test_result:TestHtmlReport


For the XGrid Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Apple XGrid is a grid solution for Apple computers that lets desktops and
dedicated servers be used in a computational grid.

The Xgrid task controller only runs on platforms where XGrid is available
(currently, only Mac OSX). Pebl uses the PyXG package to access the XGrid
controller::

    easy_install PyXg

To test the XGrid feature, find the location where pebl was installed by
easy_install and navigate to the src/pebl/test.manual directory.  There, create
a file called xgridconfig.txt and include the relevant configuration
parameters. The file should look like::

    [xgrid]
    controller = your.controller.com
    password = yourpassword
    grid = gridnumber
    pollinterval = 30

Then, execute the test_xgrid.py test::

    python test_xgrid.py xgridconfig.txt

Pebl will create and run 10 short learners over the XGrid. It will print some
information about submitting and retrieving data from the Xgrid controller and
finally print a list of machines where the tasks ran.

For the IPython1 Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
IPython1 is the next version of the popular IPython shell that also includes an
interactive, clustering solution. Pebl can use IPython1 to execute learners in
parallel.

You will need to install both IPython and IPython1.  IPython1 is in active
development and pebl requires a specific version. Once, IPython1 is oficially
released, we will use that package::

    easy_install ipython

    svn co -r 2815 http://ipython.scipy.org/svn/ipython/ipython1/trunk ipython1-2815
    cd ipython1-2815
    sudo python setup.py install

To test the IPython1 feature, make sure that IPython1's ipcluster is in the
path and run::

    nosetests -v pebl.test.test_taskcontroller:TestIPython1TC

The test will create three local IPython1 engines and run tasks on them. The
test cannot, unfortunately, terminate the engines and that needs to be done
manually. Simply run 'ps' and terminate the appropriate processes.

For the EC2 Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Amazon EC2 is an on-demand cloud computing solution from Amazon. It allows
users to rent computing power on an as-needed basis. Pebl can reserve, create,
use and terminate EC2 instances automatically. More information available at
http://aws.amazon.com/ec2/

Before you can use Amazon's EC2 platform, you need to register with Amazon and
create the required authentication credentials.  Consult the `Getting Started
Guide
<http://docs.amazonwebservices.com/AWSEC2/2008-02-01/GettingStartedGuide/>`_ at
Amazon for further information.

Pebl uses the boto package to interact with EC2::

    easy_install boto

Also see the instructions above for installing dependencies for the IPython1
Task Controller (which is required by the EC2 Task Controller).

To test the EC2 feature, find the location where pebl was installed by
easy_install and navigate to the src/pebl/test.manual directory.  There, create
a file called ec2config.txt and include the relevant configuration
parameters. The file should look like::

    [EC2]
    access_key = YOUR_AMAZON_ACCESSKEY
    secret_access_key = YOUR_AMAZON_SECRET_ACCESS_KEY

    ami = ami-66a3470f    # or any AMI with pebl, IPython1 and svn installed
    key_name = keyname-to-use
    credential = ~/foo/private-key-to-use
    
Then, execute the test_ec2.py test::

    python test_ec2.py ec2config.txt

Pebl will reserve and use 3 EC2 instances, upgrade the version of pebl
installed, run 10 shorts tasks on them and terminate the instances when
finished. If all works sucessfully, Pebl will print the hostnames of the
machines used.

For developing Pebl
^^^^^^^^^^^^^^^^^^^

Pebl developers will also need nose for testing and sphinx for generating html
documentation::


    easy_install nose
    easy_install sphinx

