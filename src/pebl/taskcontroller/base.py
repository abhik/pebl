import copy

#
# Tasks and their results
#
class Task(object):
    def run(self): pass

    def split(self, count):
        return [self] + [copy.deepcopy(self) for i in xrange(count-1)]

class DeferredResult(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    @property
    def result(self): pass
    
    @property
    def finished(self): pass

#
# Base Controllers
#
class _BaseController(object):
    def __init__(self, *args, **kwargs): pass
    def run(self, tasks): pass

class _BaseSubmittingController(_BaseController):
    def submit(self, tasks): pass
    def retrieve(self, deferred_results): pass

    def run(self, tasks):
        return self.retrieve(self.submit(tasks))
