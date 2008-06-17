import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages, Extension
import numpy

setup(
    name='Pebl',
    version='0.9.8',
    description='Python Environment for Bayesian Learning',
    package_dir={'': 'src'},
    packages=find_packages('src'),

    ## Package metadata.. for upload to PyPI
    author='Abhik Shah',
    author_email='abhikshah@gmail.comm',
    url='http://pebl-project.googlecode.com',

    # required dependencies
    install_requires=[
        'numpy >= 1.0.3',       # matrices, linear algebra, etc
        'nose >= 0.9',          # testing framework
        'pydot',                # to output network as dot file
        'pyparsing >= 1.4.7',   # required by pydot but not specified in its setup
        'simplejson',           # for html results
    ],
    
    # data files, resources, etc
    include_package_data = True,

    # tests
    test_suite = 'nose.collector',

    # scripts
    entry_points = {
        'console_scripts': [
            'pebl = pebl.pebl_script:main'
        ]
    },

    # C extension modules
    ext_modules = [
        Extension('pebl._network', sources=['src/pebl/_network.c']),
        Extension('pebl._cpd', sources=['src/pebl/_cpd.c'], include_dirs=[numpy.get_include()]),
    ],
)
