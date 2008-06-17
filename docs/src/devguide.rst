.. _devguide:

Developer's Guide
==================

This page contains information useful for developing pebl (adding code to it),
not for using it. For instructions on using pebl, consult the :ref:`tutorial`.

Setting up a development environment for Pebl
----------------------------------------------

1. Checkout pebl code from the subversion repository::


    svn co http://pebl-project.googlecode.com/svn/trunk pebl

 
2. Install development-related dependencies. Install nose (:command:`easy_install nose`)
   for unit tests and sphinx (:command:`easy_install sphinx`) for creating
   documentation.


3. Install pebl in development mode. This allows you to make changes to the
   source code and have it reflected in the "installed" version of pebl
   immediately.::


    sudo python setup.py build develop


You can now modify pebl source code and use the changes simply by importing
pebl. If you modify C or C++ code, you must run :command:`python setup.py
build` again.

Coding guildelines
------------------
1. Style guidelines

    We follow the python community standard :pep:`8` for coding style although
    in-project consistency is more important that strict compliance with
    :pep:`8`.

2. Using pebl.config

    Use the :mod:`pebl.config` module to parameterize your code.  Configuration
    should be read during object initialization (in __init__) even if it is not
    used until later.  Any changes to configuration parameters after object
    intialization should not affect your object. 

3. Testing

    We're not religious about following strict unit testing methodologies but ALL
    critical code should be accompanied by tests (unit tests are preferred but
    doctests are also accepted).  Run the unit tests by running
    :command:`nosetests -v pebl.test` from any directory. Run unit tests
    frequently during development and especially before commiting any code. You
    can place test to be run manually in pebl/test.manual but automated unit
    tests are strongly preferred.

Bug Reports
-----------

Use the Issues tab on the Google code site for all bug reports and proposed
enhancements.  When closing a bug, include the subversion revison that
resolves the bug in the comments.

Committing code
---------------

Before you can commit code, I will have to you to the developers list in Google
code. Please email me for this.

Thanks dude
-----------

And finally, thank you for considering contributing code to Pebl. I envision pebl to be a community resource that can serve as a good base for further research into Bayesian networks. Feel free to contact me with any questions or comments (abhikshah@gmail.com).
