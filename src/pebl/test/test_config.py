r"""
Doctests for pebl.config
=========================

>>> import os.path
>>> import sys
>>> from pebl import config
>>> from pebl.test import testfile

Define parameters
------------------

>>> config.StringParameter('test.param0', 'a param', default='foo').name
'test.param0'

>>> config.StringParameter('test.param1', 'a param', config.oneof('foo', 'bar')).name
'test.param1'

>>> config.IntParameter('test.param2', 'a param', default=20).name
'test.param2'

>>> config.IntParameter('test.param3', 'a param', config.atmost(100)).name
'test.param3'

>>> config.IntParameter('test.param4', 'a param', config.atleast(100)).name
'test.param4'

>>> config.IntParameter('test.param5', 'a param', config.between(10,100)).name
'test.param5'

>>> config.IntParameter('test.param6', 'a param', lambda x: x == 50).name
'test.param6'

>>> config.FloatParameter('test.param7', 'a param', config.between(1.3, 2.7)).name
'test.param7'


Test getting/setting parameter values
--------------------------------------

>>> config.get('test.param0')
'foo'
>>> config.get('tEST.paRam0')
'foo'
>>> config.get('TEST.PARAM0')
'foo'
>>> config.get('test.param2')
20
>>> config.set('test.param2', "10")
>>> config.get('test.param2')
10
>>> isinstance(config.get('test.param2'), int)
True
>>> config.set('test.param2', "foo")
Traceback (most recent call last):
...
Exception: Cannot convert value to required datatype: invalid literal for int() with base 10: 'foo'
>>> config.set('test.param100', 50)
Traceback (most recent call last):
...
KeyError: 'Parameter test.param100 is unknown.'
>>> config.set('test.param4', 150)
>>> config.set('test.param4', 50)
Traceback (most recent call last):
...
Exception: Value 50 is not valid for parameter test.param4. Parameter value should be at least 100.
>>> config.set('test.param5', 50)
>>> config.set('test.param5', 5)
Traceback (most recent call last):
...
Exception: Value 5 is not valid for parameter test.param5. Parameter value should be between 10 and 100.
>>> config.get('test.param5') 
50
>>> config.set('test.param6', 49)
Traceback (most recent call last):
...
Exception: Value 49 is not valid for parameter test.param6. error unknown
>>> config.set('test.param6', 50)
>>> config.set('test.param7', .50)
Traceback (most recent call last):
...
Exception: Value 0.5 is not valid for parameter test.param7. Parameter value should be between 1 and 2.
>>> config.set('test.param7', 1.50)
>>> config.set('test.param7', "1.50")
>>> config.set('test.param7', "1.5e0")
>>> config.get('test.param7')
1.5
>>> isinstance(config.get('test.param7'), float)
True
>>> config.set('test.param1', 'foo')
>>> config.set('test.param1', 'bar')
>>> config.set('test.param1', 'foobar')
Traceback (most recent call last):
...
Exception: Value foobar is not valid for parameter test.param1. Parameter value should be one of {foo, bar}.
>>> config.read(testfile('config1.txt'))
>>> config.read(testfile('config2.txt'))
Traceback (most recent call last):
...
Exception: 2 errors encountered:
Value 12.0 is not valid for parameter test.param7. Parameter value should be between 1 and 2.
Value 150 is not valid for parameter test.param5. Parameter value should be between 10 and 100.

Test the creation of configobj
-------------------------------

>>> config.StringParameter('test.param0', 'a param', default='foo').name
'test.param0'
>>> config.StringParameter('test.param1', 'a param', default='foo').name
'test.param1'
>>> config.IntParameter('test1.param1', 'a param', default=5).name
'test1.param1'
>>> config.set('test.param1', 'foobar')
>>> params = [config._parameters.get(x) for x in ('test.param0', 'test.param1', 'test1.param1')]
>>> config.configobj(params).write(sys.stdout)
[test]
param1 = foobar
param0 = foo
<BLANKLINE>
[test1]
param1 = 5
<BLANKLINE>
>>>

"""

if __name__ == '__main__':
    from pebl.test import run
    run()
