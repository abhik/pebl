.. highlight:: python
   :linenothreshold: 3

.. _tutorial:


Tutorial
========

This tutorial is organized as a series of examples that highlight some of
Pebl's various features.  It is assumed that the reader is familiar with
Bayesian networks and the python language and has read the :ref:`intro`.

Pebl includes a python library and a command line application that can be used
with a configuration file.  The pebl application is limited compared to the
library but requires no programming.  Each example in this tutorial will
include a python script and a pebl configuration file that runs the same 
analysis (when possible).

.. note:: This tutorial uses Pebl 0.9.9

Introducing the Problem
-----------------------

Bayesian networks have been used to model complex phenomena with non-linear,
multimodal relationships between high-dimensional variables. When used to model
gene regulatory networks, nodes usually represent the expression profile of
genes while edges represent dependencies between them. The learned networks can
be interpreted as causal models explaining the data and can hint at the
underlying biological mechanisms and functions.

For this tutorial, we use the Cell Cycle data from Spellman, et. al [1] as an
example dataset.  This dataset contains 76 gene expression measurements of 6177 
S. cerevisiae ORFs. The experiments include six time series using different
cell cycle synchronization methods. In this example, we ignore the temporal
aspect of the dataset and treat each measurement as an independent sample from
the underlying biological phenomena.  Spellman et al. identified 800 genes as
cell cycle dependent and we use a small 12 gene subset of that (as show in Fig
8.11 of [2]).

`pebl-tutorial-data1.txt <_static/tutorial/pebl-tutorial-data1.txt>`_ contains
the gene expression measurements for our 12 genes.  Each row contains one
sample (the gene expression data from one microarray assay) and each column
contains the gene expression profile for a given gene over the 76 measurements.
The first row containing the variable names (the gene associated with the
measured ORF) is required for all pebl data files.


First Example
-------------

This is the simplest analysis in Pebl::

>>> from pebl import data
>>> from pebl.learner import greedy
>>> dataset = data.fromfile("pebl-tutorial-data1.txt")
>>> dataset.discretize()
>>> learner = greedy.GreedyLearner(dataset)
>>> ex1result = learner.run()
>>> ex1result.tohtml("example1-result")

The code above does the following:

 * Imports the required modules (lines 1-2)
 * Loads the dataset (line 3)
 * Discretizes the continuous values in the dataset (line 4)
 * Creates and runs a greedy learner with default parameters (lines 5-6)
 * Creates a html report of the results (line 7)

The same analysis can be run with the following configuration file::

    [data]
    filename = pebl-tutorial-data1.txt
    discretize = 3

    [learner]
    type = greedy.GreedyLearner

    [result]
    format = html
    outdir = example1-result

To use the configuration file above, save it as a text file (config1.txt) and
run the pebl application::

    $/usr/local/bin/pebl run config1.txt

.. note:: The location of the pebl application may be different based on your installation method

The result of this example is available `here
<_static/tutorial/example1-result/index.html>`_.  Keep in mind that structure
learning of Bayesian networks uses stochastic methods and the results from
different runs will not be identical. Also, the results from this short run are
not realistic or spectacular; they do, however, serve as a good demostration of
the features of the html report.

The result is organized intro three tabs. The first tab shows the log scores
for the top networks and some overall statistics.  The second tab shows
the top 10 networks found and the last tab shows consensus networks at
different confidence thresholds.  The consensus networks are built using
estimated marginal posterior probabililty of each edge.


Pebl's Data File Format
-----------------------

Pebl uses tab-delimited text files for its data.  Each column represents a
variable and each row represents a sample or observation.  The data file can
contain any number of comment rows that begin with a "#".  The first
non-comment row is expected to be a header row that specifies the name and type
of each variable. Pebl supports continuous, discrete and class variables. The
three variable types have different header formats as shown below:

+------------+--------------------------------------------+-------------------------------+
| Type       | Header Format                              | Examples                      |
+============+============================================+===============================+
| continuous + <variable-name>[,continuous]               | CLN2                          |
|            |                                            | CLN1,continuous               |
+------------+--------------------------------------------+-------------------------------+
| discrete   | <variable-name>,discrete(<variable-arity>) | CLN2,discrete(2)              |
|            |                                            | CLN1,discrete(3)              |
+------------+--------------------------------------------+-------------------------------+
| class      | <variable-name>,class(<class-labels>)      | CLN2,class(low,high)          |
|            |                                            | phenotype,class(cancer,normal)|
+------------+--------------------------------------------+-------------------------------+

.. note:: Although Pebl accepts continuous values in the data file, they must be discretized before use.

Each measured value can be annotated with two indicators.  Append or prepend a
"!" to the value to indicate that the variable was intervened upon for that
sample or observation.  The intervention can be a gene knockdown, RNA silencing
or any perturbation that directly affect the value for that variable. Missing
values are indicated by using "X". This can be the result of a scratch on a
micrarray slide or, if all the rows for a variable include "X", a variable that
wasn't measured.

Each sample (row) can have a name which should be in the first column. This is
not used in learning a Bayesian network, but can be used to create subsets of
the data based on the sample names.

`pebl-tutorial-data2.txt <_static/tutorial/pebl-tutorial-data2.txt>`_  is the
discretized version of our data file with sample names and was created with the
following script::

>>> from pebl import data
>>> dataset = data.fromfile("pebl-tutorial-data1.txt")
>>> dataset.discretize(numbins=3)
>>> for i,s in enumerate(dataset.samples):
>>>    s.name = "sample-%d" % i
>>> dataset.tofile("pebl-tutorial-data2.txt")


Second Example
--------------

In the first example, we used the default parameters for the greedy learner
(1000 iterations) which is inadequate for a dataset of this size. In this
example, we use custom stopping criteria::

>>> from pebl import data, result
>>> from pebl.learner import greedy
>>> dataset = data.fromfile("pebl-tutorial-data2.txt")
>>> learner1 = greedy.GreedyLearner(dataset, max_iterations=1000000)
>>> learner2 = greedy.GreedyLearner(dataset, max_time=120) # in seconds
>>> result1 = learner1.run()
>>> result2 = learner2.run()
>>> merged_result = result.merge(result1, result2)
>>> merged_result.tohtml("example2-result")

The code above does the following:

 * Imports the required modules (lines 1-2)
 * Loads the discretized dataset (line 3)
 * Creates and runs two greedy learners with specified stopping criteria (lines 4-7)
 * Merges the two learner results and creates html report (lines 8-9)

A Pebl configuration file can be used to create multiple learners but they must
be of the same type and use the same parameters (stopping criteria in this
case). Thus, it is not possible to replicate the above code with a
configuration file but it can be approximated::

    [data]
    filename = pebl-tutorial-data2.txt

    [learner]
    type = greedy.GreedyLearner
    numtasks = 2

    [greedy]
    max_iterations = 1000000

    [result]
    format = html
    outdir = example2-result


Third Example
-------------

For large datasets, we might wish to do multiple learner runs and use different
learners. The following example creates and runs 5 greedy and 5 simulated
annealing learners::

>>> from pebl import data, result
>>> from pebl.learner import greedy, simanneal
>>> dataset = data.fromfile("pebl-tutorial-data2.txt")
>>> learners = [ greedy.GreedyLearner(dataset, max_iterations=1000000) for i in range(5) ] + \
>>>            [ simanneal.SimulatedAnnealingLearner(dataset) for i in range(5) ]
>>> merged_result = result.merge(learner.run() for learner in learners)
>>> merged_result.tohtml("example3-result")

The code above is similar to the last example except that we create a list of
10 learners of two different types. The corresponding configuration file has
the same caveat as in the previous example::

    [data]
    filename = pebl-tutorial-data2.txt

    [learner]
    type = greedy.GreedyLearner
    numtasks = 10

    [greedy]
    max_iterations = 1000000

    [result]
    format = html
    outdir = example3-result


Fourth Example
--------------

In the previous example, we run 10 learners serially.  We can use Pebl's
taskcontroller package to run these learners in parallel::

>>> from pebl import data, result
>>> from pebl.learner import greedy, simanneal
>>> from pebl.taskcontroller import multiprocess
>>> dataset = data.fromfile("pebl-tutorial-data2.txt")
>>> learners = [ greedy.GreedyLearner(dataset, max_iterations=1000000) for i in range(5) ] + \
>>>            [ simanneal.SimulatedAnnealingLearner(dataset) for i in range(5) ]
>>> tc = multiprocess.MultiProcessController(poolsize=2)
>>> results = tc.run(learners)
>>> merged_results = results.merge(merged_results)
>>> merged_results.tohtml("example4-result")
>>> merged_result.tohtml("example2-result")

In this example, we import the multiprocess module (line 3), create a
multiprocess task controller with a pool size of two processes (line 7), run
the learners using the task controller (line 8) and merge the results and
create html report as before.

The corresponding configuration file (with the caveats mention in the previous
example) would be::

    [data]
    filename = pebl-tutorial-data1.txt

    [learner]
    type = greedy.GreedyLearner
    numtasks = 10

    [greedy]
    max_iterations = 1000000

    [taskcontroller]
    type = multiprocess.MultiProcessController
    
    [multiprocess]
    poolsize = 2

    [result]
    format = html
    outdir = example2-result


Pebl provides three other task controllers:
 * :mod:`pebl.taskcontroller.xgrid` for using Apple's XGrid
 * :mod:`pebl.taskcontroller.ipy1` for using an Ipython1 cluster 
 * :mod:`pebl.taskcontroller.ec2` for using Amazon EC2 

All task controllers can be used with the pebl application and configuration
file and the only difference between their usage are the parameters they
require. Thus, Pebl allows one to do preliminary analysis on their desktop with
perhaps the multiprocess task controller and then do the full analysis using an
XGrid or Amazon's EC2 by simply changing one line of code or a few lines in a
configuration file. The EC2 task controller is an especially attractive option
for large analysis tasks because it allows one to rent the computing resources
on an as-needed basis and without any cluster installation or configuration.


A Note on Interpreting the Results
----------------------------------

There is no principled way to determine the optimal stopping criteria or
simulated annealing parameters for analyzing a given dataset.  One common
strategy is to construct consensus networks that show network features found
with high confidence. Pebl's html reports show such "model-averaged" networks in
the third tab and the :mod:`pebl.posterior` module has methods for creating
these programatically. 

Another common strategy is to check for stability of results. You begin with
some learning, save the results, do futher learning, merge the two results and
see if the top networks and consensus networks have changed much. If they
remain relatively stable, you can assume that you've reached a good solution.
Keep in mind, however, that you can never guarantee that you've found the
optimal network (or that there is a singular optimal network to be found) since
structure learning of Bayesian network is a known NP-Hard problem.

In the examples above, we've been creating html reports of the results but these
cannot be later merged. A better option is to save the result using the
:meth:`pebl.result.LearnerResult.tofile` method and then later read it with
:func:`pebl.result.fromfile`::

>>> from pebl import data, result
>>> result1 = learner.run()
>>> result1.tofile("result1.pebl")
>>> result1.tohtml("result1")
>>> result2 = otherlearner.run()
>>> result1 = result.fromfile("result1.pebl")
>>> merged_result = result.merge(result1, result2)
>>> merged_result.tofile("results_sofar.pebl")

A third strategy is to calculate a p-value for each scored network. This will be added to the tutorial shortly.

More Coming Soon
----------------

I will be adding examples for using prior knowledge and for calculating p-values using a bootstrapping approach.

Learning More
-------------

This tutorial should have given you an overview of using Pebl. For further
information about specific components, consult the :ref:`apiref`, which
contains detailed information about all parts of pebl.  If you would like to
add code to pebl, consult the :ref:`devguide`.  Feel free to contact me (Abhik
Shah <abhikshah@gmail.com>) with any questions or comments.

Bibliography
------------
[1] Spellman et al., (1998).  Comprehensive Identification of Cell
    Cycle-regulated Genes of the Yeast Saccharomyces cerevisiae by Microarray
    Hybridization.  Molecular Biology of the Cell 9, 3273-3297. 

[2] Husmeier et al., Probabilistic Modeling in Bioinformatics and Medical
    Informatics. Springer, 2004. http://books.google.com/books?id=ND8rjHNkJ-QC
