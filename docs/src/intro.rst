.. _intro:

Pebl Introduction
==================

Pebl is a python library and command line application for learning the
structure of a Bayesian network given prior knowledge and observations.  Pebl
includes the following features:

 * Can learn with observational and interventional data
 * Handles missing values and hidden variables using exact and heuristic
   methods 
 * Provides several learning algorithms; makes creating new ones simple
 * Has facilities for transparent parallel execution
 * Calculates edge marginals and consensus networks
 * Presents results in a variety of formats

Availability
------------
Pebl is licensed under a permissive `MIT-style license
<http://pebl-project.googlecode.com/svn/trunk/LICENSE.txt>`_ and can be
downloaded from its `Google code site <http://pebl-project.googlecode.com/>`_
or from the `Python Package Index <http://pypi.python.org/pypi/pebl>`_.

Concepts   
--------
All Pebl analysis include :term:`data`, a :term:`learner` and a :term:`result`.  They may also
include :term:`prior models` and :term:`task controllers`.  

.. glossary::
    Data
        This is the set of observations that is used to score a given network.
        The data can include missing values and hidden/unobserved variables and
        observations can be marked as being the result of specific
        interventions. Data can be read from a file or created progrmatically.

    Learner
        A learner implements a specific learning algorithm. It is given some
        data, prior model and a stopping criteria and returns a :term:`result`
        object.

    Result
        A result object contains a list of the top-scoring networks found
        during a learner run and some statistics about the analysis. Results
        from different learning runs with the same data can be merged and
        visualized in various formats.

    Prior Models
        A key strength of Bayesian analysis is the ability to integrate
        knowledge with observations. A Pebl prior model specifies the prior
        belief about the set of possible networks and can include hard and soft
        constraints.

    Task Controllers
        Pebl uses task controllers to run analyses in parallel.  Users can
        utilize multiple CPU cores or computational clusters without managing
        any of the details related to parallel programming. 
