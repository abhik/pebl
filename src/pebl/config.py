import sys
from ConfigParser import ConfigParser

_parameters = {}

# validators
def between_min_and_max(min, max):
    return lambda x: x >= min and x <= max

def one_of(*values):
    return lambda x: x in values

def at_least(min):
    return lambda x: x > min

def at_most(max):
    return lambda x: x < max

class ParameterSpec:
    def __init__(self, name, description, datatype, default=None, validator=lambda x: True):
        if len(name.split('.')) > 2:
            raise Exception("Parameter name has to be of the form 'section.name' or 'name'")

        self.name = name
        self.attr_name = name[name.find(".")+1:]
        self.section = name[:name.find(".")] or 'DEFAULT'

        self.description = description
        self.datatype = datatype
        self.validator = validator
        self.value = default
        self.value_source = None


    def __repr__(self):
        return "%s = %s (%s): %s" % (self.name, self.value, self.datatype.__name__, self.description)

# has_parameter DSL (domain specific language) statement
# idea from http://elixir.ematia.de/svn/elixir/trunk/elixir/statements.py
class has_parameter_statement(object):
    def __call__(self, *args, **kwargs):
        paramspec = ParameterSpec(*args, **kwargs)
        class_locals = sys._getframe(1).f_locals
        
        class_params = class_locals.setdefault('__parameters__', [])
        class_params.append(paramspec)
        add_parameter(paramspec)

has_parameter = has_parameter_statement()


def add_parameter(paramspec):
    _parameters[paramspec.name.lower()] = paramspec

def set(name, value, value_source='config.set'):
    name = name.lower()
    
    if name not in _parameters:
        raise Exception("Parameter %s is unknown." % name)
    
    paramspec = _parameters[name]

    # try coercing value to required data type
    try:
        value = paramspec.datatype(value)
    except ValueError, e:
        raise Exception("Cannot convert value to required datatype: %s" % e.message)

    # try validating
    try:
        valid = paramspec.validator(value)
    except:
        raise Exception("Validator for %s caused an error while validating value %s" % (name, value))

    if not valid:
        raise Exception("Value %s is not valid for parameter %s" % (value, name))

    _parameters[name].value = value
    _parameters[name].value_source = value_source

def get(name, **kwargs):
    name = name.lower()

    if name in _parameters:
        return _parameters[name].value
    elif 'default' in kwargs:
        return kwargs['default']
    else:
       raise KeyError("Parameter %s not found." % name)

def read(filename):
    config = ConfigParser()
    config.read(filename)

    for section in config.sections() + ['DEFAULT']:
        for name,value in config.items(section):
            fullname = "%s.%s" % (section, name) if section != 'DEFAULT' else name
            set(fullname, value, "config file %s" % filename)

def write(filename, including_defaults=False):
    config = ConfigParser()
    params = _parameters if including_defaults else [p for p in _parameters.values() if p.value_source]

    for param in params:
        config.set(param.section, param.attr_name, param.value)

    f = open(filename, 'w')
    config.write(f)
    f.close()

def list_parameters():
    return [(p.name, p.value, p.description) for p in _parameters.values()]

def apply_parameters(obj):
    for param in obj.__parameters__:
        setattr(obj, param.attr_name, param.value)
