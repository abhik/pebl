Configuration Parameters Reference
==================================

Here are the configuration parameters supported by pebl. These can set in a
configuration file or via the config.set() function.

data
----

.. confparam:: data.discretize

	Number of bins used to discretize data. Specify 0 to indicate that data should not be discretized.
	default=0

.. confparam:: data.filename

	File to read data from.
	default=None

.. confparam:: data.text

	The text of a dataset included in config file.
	default=

evaluator
---------

.. confparam:: evaluator.missingdata_evaluator

	Evaluator to use for handling missing data.
	default=gibbs

gibbs
-----

.. confparam:: gibbs.burnin

	Burn-in period for the gibbs sampler (specified as a multiple of the number of missing values)
	default=10

.. confparam:: gibbs.stopping_criteria

	Stopping criteria for the gibbs sampler.
        
        Should be a valid python expression that evaluates to true when gibbs
        should stop. It can use the following variables:

            * iters: number of iterations
            * n: number of missing values
        
        Examples:

            * iters > n**2  (for n-squared iterations)
            * iters > 100   (for 100 iterations)
        
	default=iters > n**2

greedy
------

.. confparam:: greedy.restarting_criteria

	Restarting criteria for the GreedyLearner.
	default=restart_after_max_unimproved_iterations(500)

.. confparam:: greedy.seed

	Starting network for a greedy search.
	default=

.. confparam:: greedy.stopping_criteria

	Stopping criteria for the GreedyLearner.
	default=stop_after_max_iterations(1000)

learner
-------

.. confparam:: learner.numtasks

	Number of learner tasks to run.
	default=1

.. confparam:: learner.type

	Type of learner to use. 

    The following learners are included with pebl:
        * greedy.GreedyLearner
        * simanneal.SimulatedAnnealingLearner
        * exhaustive.ListLearner
    
	default=greedy.GreedyLearner

listlearner
-----------

.. confparam:: listlearner.networks

	List of networks to score.
	default=

multiprocess
------------

.. confparam:: multiprocess.poolsize

	Number of processes to run concurrently (0 means no limit)
	default=0

pebl
----

.. confparam:: pebl.workingdir

	Working directory for pebl.
	default=.

result
------

.. confparam:: result.filename

	The name of the result output file
	default=result.pebl

.. confparam:: result.format

	The format for the pebl result file (pickle or html).
	default=pickle

.. confparam:: result.numnetworks

	Number of top-scoring networks to save. Specify 0 to indicate that
    all scored networks should be saved.
	default=1000

simanneal
---------

.. confparam:: simanneal.delta_temp

	Change in temp between steps.
	default=0.5

.. confparam:: simanneal.max_iters_at_temp

	Max iterations at any temperature.
	default=100

.. confparam:: simanneal.seed

	Starting network for a greedy search.
	default=

.. confparam:: simanneal.start_temp

	Starting temperature for a run.
	default=100.0

taskcontroller
--------------

.. confparam:: taskcontroller.type

	The task controller to use.
	default=serial

xgrid
-----

.. confparam:: xgrid.controller

	Hostname or IP of the Xgrid controller.
	default=

.. confparam:: xgrid.grid

	Id of the grid to use at the Xgrid controller.
	default=0

.. confparam:: xgrid.password

	Password for the Xgrid controller.
	default=

.. confparam:: xgrid.peblpath

	Full path to the pebl script on Xgrid agents
	default=pebl

.. confparam:: xgrid.pollinterval

	Time (in secs) to wait between polling the Xgrid controller.
	default=60.0


