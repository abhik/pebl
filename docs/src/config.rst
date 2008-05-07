:mod:`config` -- Pebl's configuration system
=============================================

.. module:: pebl.config
    :synopsis: Pebl's configuration system

The config module defines a set of parameter types and functions to validate
user input. A module or class can define a parameter by creating an instance of
one of the Parameter classes -- it is automatically registered with the config
module. Many modules provide a fromconfig() factory function that create and
return a parametrized object.


Specifying Parameters
---------------------

A Parameter definition requires the following:

    * a name of the form section.option
      (examples: data.filename, result.format)
    * a short description
    * a validator function  

      The function has one argument: the string value of the parameter. It
      should return true if the value is valid and false otherwise.  The config
      module includes several factory functions that create
      validator functions. See section on validator factories.
    * a default value specified as a string  
       
Example parameter definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the pebl.data module::

    _pfilename = config.StringParameter(
        'data.filename',
        'File to read data from.',
        config.fileexists(),
    )

In the above example, the config.fileexists() function returns a validator
function that checks whether the file exists.

From the pebl.result module::

    _psize = config.IntParameter(
        'result.numnetworks',
        \"\"\"Number of top-scoring networks to save. Specify 0 to indicate that
        all scored networks should be saved.\"\"\",
        default=1000
    )

In the above example, The IntParameter subclass of Parameter automatically
checks whether the parameter value is an integer and raises an error if it is
not. It thus does not require an additional validator.

Parameter Types
---------------

.. autoclass:: StringParameter
.. autoclass:: IntParameter
.. autoclass:: FloatParameter


Validator Factories
-------------------

The following functions create validator functions.

.. autofunction:: between
.. autofunction:: oneof
.. autofunction:: atleast
.. autofunction:: atmost
.. autofunction:: fileexists


Using Parameters
----------------

Parameters can be set with the config.set function or in a configuration file.
The config file should be in a format compatible with Python's ConfigParser
module.

Specifying parameter values using a config file::
    
    [data]
    filename = example_data.txt

    [result]
    format=html

Specifying parameter values using config.set::

    from pebl import config
    config.set('data.filename', 'example_data.txt')
    config.set('result.format', 'html')

.. autofunction:: set


The following functions are used for reading, getting, writing and listing
parameters.

.. autofunction:: read
.. autofunction:: get
.. autofunction:: write
.. autofunction:: parameters
.. autofunction:: configobj

