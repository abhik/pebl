import os
from pebl import config

class TestConfig:
    def setUp(self):
        config.add_parameter(config.ParameterSpec('TestParams.param1', 'param 1', int, 50, config.at_least(10)))
        config.add_parameter(config.ParameterSpec('TestParams.param2', 'param 2', float, 50, config.between_min_and_max(10,200)))
        config.add_parameter(config.ParameterSpec('TestParams.param3', 'param 3', str, 'a', config.one_of('a', 'b')))

    def test_case_insensitivity(self):
        config.get('testparams.param1')
        config.get('tEstParams.parAm1')

    def test_default(self):
        assert config.get('TestParams.param1') == 50, "Setting default values"
    
    def test_validate_int(self):
        try:
            config.set('TestParams.param1', "foo")
        except:
            return

        assert 1 == 2, "Validating int"

    def test_unknown_param(self):
        try:
            config.set('TestParams.paramFOO', 10)
        except:
            return

        assert 1 == 2, "Should've raised exception on unknown param"

    def test_validate_int2(self):
        try:
            config.set('TestParams.param1', "15")
        except:
            assert 1 == 2, "Testing validators (should've coerced str to int)"
    
    def test_validate_atleast1(self):
        try:
            config.set('TestParams.param1', 100)
        except:
            assert 1 == 2, "Testing validators"

    def test_validate_atleast2(self):
        try:
            config.set('TestParams.param1', 5)
        except:
            return

        assert 1 == 2, "Validator missed invalid value"

    def test_validate_between(self):
        config.add_parameter(config.ParameterSpec('TestParams.param2', 'param 2', float, 50, config.between_min_and_max(10,200)))
        config.set('TestParams.param2', 55)
        config.set('TestParams.param2', 55.2)
    
    def test_validate_between2(self):
        try:
            config.set('TestParams.param2', 255.4)
        except:
            return 

        assert 1 == 2, "Validator missed invalid value."

    def test_validate_oneof1(self):
        config.set('TestParams.param3', 'b')
    
    def test_validate_oneof2(self):
        try:
            config.set('TestParams.param3', 'd')
        except: 
            return

        assert 1 == 2, "Validator missed invalid value"


CONFIGFILE = """
param1 = 50
param2 = "Foo"

[section1]
param1 = 15
"""

class TestConfigFile:
    def setUp(self):
        f = open("goodconfig.txt", 'w')
        f.write(CONFIGFILE)
        f.close()

        f = open("badconfig.txt", 'w')
        f.write(CONFIGFILE + "\nfoo=5")
        f.close()

        config.add_parameter(config.ParameterSpec('param1', 'param 1', int))
        config.add_parameter(config.ParameterSpec('param2', 'param 1', str))
        config.add_parameter(config.ParameterSpec('section1.param1', 'param 1', int))

    def tearDown(self):
        os.remove('goodconfig.txt')
        os.remove('badconfig.txt')

    def test_valid_configfile(self):
        try:
            config.read("goodconfig.txt")
        except:
            return

        assert 1 == 2, "Error reading valid config file"

    def test_invalid_configfile(self):
        try:
            config.read("badconfig.txt")
        except:
            return

        assert 1 == 2, "Should've raise exception on config file with unknown param"
