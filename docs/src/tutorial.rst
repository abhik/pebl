Tutorial
========

The tutorial is organized as a series of examples that highlight Pebl's various
features. For each example, you can download the datafiles used and type the
commands in python's interactive shell or copy to a file and execute it. 

Pebl's 'Hello World' example
-----------------------------

This is the simplest analysis in Pebl::

>>> from pebl import data
>>> from pebl.learner import greedy
>>> dataset = data.fromfile("example1-data.txt")
>>> learner = greedy.GreedyLearner(dataset)
>>> learner.run()
>>> learner.result.tohtml("example1-result")

The code above imports the required modules (lines 1-2), loads the data (line
3), creates and runs a Greedy Learner with its default stopping criteria (lines
4-5) and outputs the results as a set of html files (line 6).

Setting custom stopping criteria
---------------------------------

This example shows several ways of specifying stopping criteria for the
GreedyLearner::

>>> learner = greedy.GreedyLearner(dataset, stopping_criteria=greedy.stop_after_max_iterations(1000))

>>> learner = greedy.GreedyLearner(dataset, stopping_criteria=greedy.stop_after_max_seconds(600))

>>> def my_stopping_criteria(stats):
>>>     return stats.iterations > 10000 or stats.runtime > 600
>>> learner = greedy.GreedyLearner(dataset, stopping_criteria=my_stoping_criteria)

>>> learner = greedy.GreedyLearner(dataset, stopping_criteria=lambda stats: stats.runtime > 600)


Running on Apple's XGrid
------------------------

Analyses can be run in parallel using Apple's XGrid as follows::

>>> from pebl import data, result
>>> from pebl.learner import greedy
>>> from pebl.taskcontroller import xgrid
>>> dataset = data.fromfile("example1-data.txt")
>>> learner = greedy.GreedyLearner(dataset)
>>> tasks = learner.split(10)
>>> mygrid = xgrid.XGridController('sysbio.engin.umich.edu', 'password')
>>> results = mygrid.run(tasks)
>>> merged_result = result.merge(results)
>>> merged_result.tohtml("example1-result")


Learning with hidden variables
------------------------------

Learning with hidden variables is the same as without; the dataset simply needs
to be annotated to include the hidden variables::

>>> from pebl import data
>>> from pebl.learner import greedy
>>> dataset = data.fromfile("example1-data.txt")
>>> learner = greedy.GreedyLearner(dataset)
>>> learner.run()
>>> learner.result.tohtml("example1-result")




