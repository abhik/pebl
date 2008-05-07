"""Classes and functions for specifying and working with parameters."""

from __future__ import with_statement

import sys
import os.path
from ConfigParser import ConfigParser
from itertools import groupby
from time import asctime
from operator import attrgetter

from pebl.util import unzip, as_list

#
# Global list of parameters
#
_parameters = {}


#
# Validator Factories (they return validator functions)
#
def between(min, max):
    """Returns validator that checks whether value is between min and max."""
    v = lambda x: x >= min and x <= max
    v.__doc__ = "Parameter value should be between %d and %d." % (min,max)
    return v

def oneof(*values):
    """Returns validator that checks whether value is in approved list."""
    v = lambda x: x in values
    v.__doc__ = "Parameter value should be one of {%s}." % ', '.join(values)
    return v

def atleast(min):
    """Returns validator that checks whether value is > min."""
    v =  lambda x: x >= min
    v.__doc__ = "Parameter value should be at least %d." % min
    return v

def atmost(max):
    """Returns validator that checks whether value is < max."""
    v = lambda x: x <= max
    v.__doc__ = "Parameter value should be at most %d." % max
    return v

def fileexists():
    """Returns validator that checks whether value is an existing file."""
    v = lambda x: os.path.exists(x) and os.path.isfile(x)
    v.__doc__ = "Parameter value should be a file that exists."
    return v


#
# Parameter classes
#
def default_validator(x):
    return True

class Parameter:
    """Classes for configuration parameters."""

    datatype = None

    def __init__(self, name, description, validator=default_validator, default=None):
        nameparts = name.split('.')
        if len(nameparts) is not 2:
            raise Exception("Parameter name has to be of the form 'section.name'")

        self.name = name.lower()
        self.section, self.option = nameparts

        self.description = description
        self.validator = validator
        self.value = self.default = default
        self.source = None

        # add self to the parameter registry
        _parameters[self.name] = self

class StringParameter(Parameter): datatype=str
class IntParameter(Parameter): datatype=int
class FloatParameter(Parameter): datatype=float

#
# Functions for {get/set/read/write/list}ing parameters
#
def set(name, value, source='config.set'):
    """Set a parameter value.

     - name should be of the form "section.name".
     - value can be a string which will be casted to the required datatype.
     - source specifies where this parameter value was specified (config file,
       command line, interactive shell, etc).

    """

    name = name.lower()
    
    if name not in _parameters:
        msg = "Parameter %s is unknown." % name
        raise KeyError(msg)
    
    param = _parameters[name]

    # try coercing value to required data type
    try:
        value = param.datatype(value)
    except ValueError, e:
        msg = "Cannot convert value to required datatype: %s" % e.message
        raise Exception(msg)

    # try validating
    try:
        valid = param.validator(value)
    except:
        msg = "Validator for parameter %s caused an error while validating" + \
              "value %s"
        raise Exception(msg % (name, value))

    if not valid:
        raise Exception("Value %s is not valid for parameter %s. %s" % \
                (value, name, param.validator.__doc__ or 'error unknown'))

    param.value = value
    param.source = source


def get(name):
    """Returns value of parameter.
    
    Raises KeyError if parameter not found.
    Examples::
        
        from pebl import config
        config.get('data.filename')
        config.get('result.format')

    The value returned could be the default value or the latest value set using
    config.set or config.read

    """
    name = name.lower()

    if name in _parameters:
        return _parameters[name].value
    else:
        raise KeyError("Parameter %s not found." % name)


def read(filename):
    """Reads parameter from config file.

    Config files should conform to the format specified in the ConfigParser
    module from Python's standard library. A Parameter's name has two parts:
    the section and the option name.  These correspond to 'section' and
    'option' as defined in ConfigParser. 
    
    For example, parameter 'foo.bar' would be specified in the config file as::

        [foo]
        bar = 5
    
    """

    config = ConfigParser()
    config.read(filename)

    errors = []
    for section in config.sections():
        for option,value in config.items(section):
            name = "%s.%s" % (section, option)
            try:
                set(name, value, "config file %s" % filename)
            except Exception, e:
                errors.append(str(e))
    
    if errors:
        errheader = "%d errors encountered:" % len(errors)
        raise Exception("\n".join([errheader] + errors))


def write(filename, include_defaults=False):
    """Writes parameters to config file.

    If include_default is True, writes all parameters. Else, only writes
    parameters that were specifically set (via config file, command line, etc).

    """

    config = ConfigParser()
    params = _parameters.values() if include_defaults \
                                  else [p for p in _parameters.values() if p.source]

    for param in params:
        config.set(param.section, param.option, param.value)

    with file(filename, 'w') as f:
        config.write(f)


def parameters(section=None):
    """Returns list of parameters.

    If section is specified, returns parameters for that section only.
    section can be a section name or a search string to use with
    string.startswith(..) 
    
    """

    if section:
        return [p for p in _parameters.values() if p.name.startswith(section)]
    else:
        return _parameters.values()


def paramdocs(section=None, section_header=False):
    lines = []
    params = sorted(parameters(section), key=attrgetter('name'))
    lines += [".. Autogenerated by pebl.config.paramdocs at %s\n\n" % asctime()]

    for section, options in groupby(params, lambda p:p.section):
        if section_header:
            lines += ["%s\n%s\n\n" % (section, '-'*len(section))]
        
        lines += [".. confparam:: %s\n\n\t%s\n\tdefault=%s\n\n" %
                  (o.name, 
                   o.description, 
                   'None' if o.default is None else o.default) 
                  for o in options] 

    return ''.join(lines)


def configobj(params):
    """Given a list of parameters, returns a ConfigParser object.

    This function can be used to convert a list of parameters to a config
    object which can then be written to file.

    """
    if isinstance(params, list):
        params = dict((p.name, p.value) for p in params)

    configobj = ConfigParser()
    for key,value in params.items():
        section,name = key.strip().split('.')
        if section not in configobj.sections():
            configobj.add_section(section)
        configobj.set(section, name, value)

    return configobj
