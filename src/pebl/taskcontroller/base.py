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

    # For synchronous task controllers (like serial and multiprocess), submit
    # simply runs (blocking). Since the result of submit is a real result and
    # not a deferred result, retrieve simply returns the results that were
    # passed in. This let's synchronous and asynchronous task controllers have
    # the same interface.
    def submit(self, tasks):
        return self.run(tasks)
    def retrieve(self, deferred_results):
        return deferred_results

class _BaseSubmittingController(_BaseController):
    def submit(self, tasks): pass
    def retrieve(self, deferred_results): pass

    def run(self, tasks):
        return self.retrieve(self.submit(tasks))
