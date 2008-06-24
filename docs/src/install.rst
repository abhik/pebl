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

.. note:: The current version of Pebl is 0.9.9.

If you have downloaded the source code for Pebl (or installing pebl from svn),
you can run :command:`sudo python setup.py install` from pebl's root directory
instead.

Installing optional dependencies
---------------------------------

Certain features of pebl require additional dependencies. You only need to
install these if you need the optional features.

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


For the XGrid Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Xgrid task controller only runs on platforms where XGrid is available
(currently, only Mac OSX). Pebl uses the PyXG package to access the XGrid
controller::

    easy_install PyXg


For the IPython1 Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will need to install both IPython and IPython1.  IPython1 is in active
development and pebl requires a specific version. Once, IPython1 is oficially
released, we will use that package::

    easy_install ipython

    svn co -r 2815 http://ipython.scipy.org/svn/ipython/ipython1/trunk ipython1-2815
    cd ipython1-2815
    sudo python setup.py install


For the EC2 Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you can use Amazon's EC2 platform, you need to register with Amazon and
create the required authentication credentials.  Consult the `Getting Started
Guide
<http://docs.amazonwebservices.com/AWSEC2/2008-02-01/GettingStartedGuide/>`_ at
Amazon for further information.

Pebl uses the boto package to interact with EC2::

    easy_install boto

Also see the instructions above for installing dependencies for the IPython1
Task Controller (which is required by the EC2 Task Controller).


For developing Pebl
^^^^^^^^^^^^^^^^^^^

Pebl developers will also need nose for testing and sphinx for generating html
documentation::


    easy_install nose
    easy_install sphinx

