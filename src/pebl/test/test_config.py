import os.path
import sys
from tempfile import NamedTemporaryFile

from pebl import config
from pebl.test import testfile


def should_raise_exception(param, value):
    try:
        config.set(param, value)
    except:
        assert True
    else:
        assert False

class TestConfig:
    def setUp(self):
        config.StringParameter('test.param0', 'a param', default='foo')
        config.StringParameter('test.param1', 'a param', config.oneof('foo', 'bar'))
        config.IntParameter('test.param2', 'a param', default=20)
        config.IntParameter('test.param3', 'a param', config.atmost(100))
        config.IntParameter('test.param4', 'a param', config.atleast(100))
        config.IntParameter('test.param5', 'a param', config.between(10,100))
        config.IntParameter('test.param6', 'a param', lambda x: x == 50)
        config.FloatParameter('test.param7', 'a param', config.between(1.3, 2.7))


    def test_get1(self):
        assert config.get('test.param0') == 'foo'

    def test_get2(self):
        assert config.get('tEST.paRam0') == 'foo'

    def test_get3(self):
        assert config.get('test.param2') == 20

    def test_get4(self):
        config.set('test.param2', "10")
        assert isinstance(config.get('test.param2'), int)
        assert config.get('test.param2') == 10

    def test_set1(self):
        should_raise_exception('test.param2', 'foo')

    def test_set2(self):
        should_raise_exception('test.param100', 50)

    def test_set3(self):
        config.set('test.param4', 150) # no exception
        should_raise_exception('test.param4', 50)

    def test_set4(self):
        config.set('test.param5', 50) # no exception
        should_raise_exception('test.param5', 5)
        assert config.get('test.param5') == 50

    def test_set5(self):
        should_raise_exception('test.param6', 49)

    def test_set6(self):
        should_raise_exception('test.param7', .50)
   
    def test_set7(self):
        config.set('test.param7', 1.50)
        config.set('test.param7', "1.50")
        config.set('test.param7', "1.5e0")
        assert config.get('test.param7') == 1.5
        assert isinstance(config.get('test.param7'), float)

    def test_set8(self):
        config.set('test.param1', 'foo')
        config.set('test.param1', 'bar')
        should_raise_exception('test.param1', 'foobar')

    def test_config1(self):
        config.read(testfile('config1.txt'))

    def test_config2(self):
        try:
            config.read(testfile('config2.txt'))
        except: 
            assert True
        else: 
            assert False

    def test_configobj1(self):
        expected = \
"""[test]
param1 = foo
param0 = foo

[test1]
param1 = 5

"""

        config.IntParameter('test1.param1', 'a param', default=5)
        config.set('test.param1', 'foo')
        params = [config._parameters.get(x) for x in ('test.param0', 'test.param1', 'test1.param1')]

        tmpfile = NamedTemporaryFile(prefix="pebl.test")
        config.configobj(params).write(tmpfile)
        
        tmpfile.file.seek(0)
        actual = tmpfile.read()
        assert actual == expected

