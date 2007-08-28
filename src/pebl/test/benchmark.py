# Want code to be py2.4 compatible. So, can't use relative imports.
import sys
sys.path.insert(0, "../")

import os, os.path
import data, network
from learners import greedy

def benchmark_datafiles():
    benchdata_dir = os.path.join(os.path.dirname(__file__), "benchdata")
    for filename in (f for f in os.listdir(benchdata_dir) if f.startswith('benchdata')):
        yield os.path.join(benchdata_dir, filename)

def run_benchmarks(datafile):
    dat = data.fromfile(datafile)
    l = greedy.GreedyLearner(dat)
    l.execute()

if __name__== '__main__':
    for datafile in benchmark_datafiles():
        run_benchmarks(datafile)

