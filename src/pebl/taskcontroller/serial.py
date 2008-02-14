from pebl.taskcontroller.base import _BaseController

class SerialController(_BaseController):
    def run(self, tasks):
        return [t.run() for t in tasks]
