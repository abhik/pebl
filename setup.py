import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages, Extension, Feature
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, \
                             DistutilsPlatformError
import numpy

BUILD_EXT_WARNING = """
WARNING: The C extensions could not be compiled. 
         Pebl will run normally but will be slower.

Below is the output showing how the compilation failed:
"""

long_desc = """
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
"""

# This class allows C extension building to fail.
# from http://simplejson.googlecode.com/svn/trunk/setup.py
class ve_build_ext(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError, x:
            self._unavailable(x)

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError), x:
           self._unavailable(x)

    def _unavailable(self, exc):
         print '*'*70
         print BUILD_EXT_WARNING
         print exc
         print '*'*70

# C extension modules (as an optional feature)
speedymodules = Feature(
    "Optional speedier C modules.",
    standard = True,
    ext_modules = [
        Extension('pebl._network', sources=['src/pebl/_network.c']),
        Extension('pebl._cpd', sources=['src/pebl/_cpd.c'], 
                  include_dirs=[numpy.get_include()]),
    ]
)

setup(
    name='pebl',
    version='1.0',
    description='Python Environment for Bayesian Learning',
    long_description = long_desc,
    package_dir={'': 'src'},
    packages=find_packages('src'),

    ## Package metadata.. for upload to PyPI
    author='Abhik Shah',
    author_email='abhikshah@gmail.comm',
    url='http://pebl-project.googlecode.com',
    download_url='http://pypi.python.org/pypi/pebl',
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],

    # required dependencies
    install_requires=[
        # 'numpy >= 1.0.3',     # matrices, linear algebra, etc
        'pydot',                # to output network as dot file
        'pyparsing >= 1.4.7',   # required by pydot but not specified in its setup
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

    # C extension modules (as an optional feature)
    features = { 'speedups': speedymodules },

    # build extensions optionally
    cmdclass={'build_ext': ve_build_ext},
)
