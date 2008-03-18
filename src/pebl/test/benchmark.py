import os, os.path
from pebl import data, network
from pebl.learner import greedy

def benchmark_datafiles(dir=None):
    benchdata_dir = dir or os.path.join(os.path.dirname(__file__), "benchdata")
    for filename in (f for f in os.listdir(benchdata_dir) if f.startswith('benchdata.')):
        yield os.path.join(benchdata_dir, filename)

def run_benchmarks(datafile):
    print datafile
    dat = data.fromfile(datafile)
    l = greedy.GreedyLearner(dat)
    l.run()

def run_all_benchmarks(dir=None):
    for datafile in benchmark_datafiles(dir):
        run_benchmarks(datafile)
    
if __name__== '__main__':
    run_all_benchmarks()
