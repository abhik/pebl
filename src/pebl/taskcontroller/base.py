from __future__ import with_statement
import os, os.path
import shutil
import tempfile
import copy

from pebl import result

#
# Tasks
#
class Task(object):
    def _prepare_config(self, workingdir_is_tmp):
        self.cwd = tempfile.mkdtemp('pebl')
        configfile = os.path.join(self.cwd, 'config.txt')
        
        # generate config object
        co = self.toconfig()

        # configure workingdir
        if workingdir_is_tmp:
            if not co.has_section('pebl'):
                co.add_section('pebl')
            co.set('pebl', 'workingdir', self.cwd)

        # configure result outputting
        if not co.has_section('result'):
            co.add_section('result')
        co.set('result', 'format', 'pickle')
        co.set('result', 'filename', 'result.pebl')
        
        # move customlearner file (if any) to tempdir
        if ':' in co.get('learner', 'type'):
            cfile = co.get('learner', 'type').split(':')[0]
            shutil.copy(cfile, self.cwd)

        # finally, write out the configfile
        co.write(open(configfile, 'w'))

    def run(self):
        pass

    def toconfig(self):
        pass

    def split(self, count):
        return [self] + [copy.deepcopy(self) for i in xrange(count)-1]

class DeferredResult(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    @property
    def result(self):
        pass

    @property
    def finished(self):
        return ''

#
# Base Controller
#
class _BaseController(object):
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def run(self, tasks):
        pass


