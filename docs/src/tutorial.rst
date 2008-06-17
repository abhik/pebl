.. highlight:: python
   :linenothreshold: 3

.. _tutorial:

Tutorial
========

This tutorial is organized as a series of examples that highlight Pebl's various
features. For each example, you can type the commands in python's interactive
shell or copy to a file and execute it. 

Pebl's data format
------------------

Pebl reads data from tab-delimited text files (like the following example):

==================  ==================  =================  ===========================
 # this is a comment.
--------------------------------------------------------------------------------------
 var1,discrete(3)    var2,discrete(2)    var3,continuous    var4,class(normal,cancer)
 0!                  X                   3.45               normal
 X                   X                  -1.20!              normal
 1                   X                   5.61               cancer
 # this is also a comment.
--------------------------------------------------------------------------------------
 2                   X                   2.12               normal
 1                   X                  -5.03               cancer
 0                   X                   0.12               cancer
==================  ==================  =================  ===========================


The file above includes 4 variables and 6 samples.  You can create this file in
a text editor or in a spreadsheet application (like Microsoft Excel) and save
it as Tab-delimited text file.

Pebl ignores all lines beginning with a '#' and these comment lines can be
anywhere in the file.  All variables must be given a name and a type. Pebl supports three types of variables: discrete, continuous and class variables.  Discrete variables must specify the arity of the variable (number of possible values) in parenthesis and class variables must specify the possible labels, also in parenthesis.

The 'X' in the datafile indicates that the value is missing and a '!' indicates that the variable was intervened upon (this requires a different scoring algorithm).  Variables can include any number of missing values or can include all missing values (making it a hidden or latent variable).  Note that althought pebl allows continuous values in the datafile, it cannot learn with them. Continuous variable must be discretized using the Dataset.discretize method.


Pebl's 'Hello World' example
-----------------------------

This is the simplest analysis in Pebl::

>>> from pebl import data
>>> from pebl.learner import greedy
>>> dataset = data.fromfile("example1-data.txt")
>>> learner = greedy.GreedyLearner(dataset, max_time=60)
>>> learner.run()
>>> learner.result.tohtml("example1-result")

The code above imports the required modules (lines 1-2), loads the data (line
3), creates and runs a Greedy Learner with a maximum runtime of 60 seconds
(lines 4-5) and outputs the results as a set of html files (line 6).

You can also run the analysis using the pebl command line application and a config file.
The config file for this example would be::

    [data]
    filename = example1-data.txt

    [learner]
    type = greedy.GreedyLearner

    [greedy]
    max_time = 60

    [result]
    format = html
    outputdir = example1-result

Then simply run::
    
    pebl run example1-config.txt
    

Setting stopping and restarting criteria
----------------------------------------

Restarting criteria determines when the GreedyLearner restarts the search with a
random seed (this allows the learner to escape from local maximas) while the
stopping criteria determines when the learner stops.

This example shows several ways of specifying stopping/restarting criteria for the
GreedyLearner::

>>> learner = greedy.GreedyLearner(dataset, max_iterations=1000)
>>> learner = greedy.GreedyLearner(dataset, max_time=60)
>>> learner = greedy.GreedyLearner(dataset, max_time=60, max_unimproved_iterations=500)

Related module reference: :mod:`pebl.learner.greedy`

Running learners in parallel
----------------------------

Pebl allows you to take advantage of clusters or grids that you have access to.  Pebl's taskcontroller package supports parallel processing over multiple processes, Apple's XGrid, an IPython1 cluster and over Amazon's EC2 platform.

For example, analysis can be run in parallel using Apple's XGrid as follows::

>>> from pebl import data, result
>>> from pebl.learner import greedy
>>> from pebl.taskcontroller import xgrid
>>> dataset = data.fromfile("example1-data.txt")
>>> learners = [greedy.GreedyLearner(dataset) for i in range(10)]
>>> mygrid = xgrid.XGridController('controller_ip', 'password')
>>> results = mygrid.run(tasks)
>>> merged_result = result.merge(results)
>>> merged_result.tohtml("example1-result")

The code above creates 10 learners (line 5), creates a XGridController (line 6) and runs the learners on the XGrid (line 7). Finally, the 10 results are merged and displayed as a set of html files (lines lines 8-9)

To run using a different taskcontroller, simply create a different taskcontroller (line 6). The rest of the code stays the same. You can even control which taskcontroller is used by using a config parameter, allowing you to write code that can easily adapt to whatever computational resources are available.

Related module references: 
 
 * :mod:`pebl.taskcontroller.serial`
 * :mod:`pebl.taskcontroller.multiprocess`
 * :mod:`pebl.taskcontroller.xgrid`
 * :mod:`pebl.taskcontroller.ipy1`
 * :mod:`pebl.taskcontroller.ec2`
 
Learning More
-------------

This tutorial should have given you an overview of using Pebl. For further information about specific components, consult the :ref:`apiref`, which contains detailed information about all parts of pebl.  If you would like to add code to pebl, consult the :ref:`devguide`.  Feel free to contact me (Abhik Shah <abhikshah@gmail.com>) with any questions or comments.

