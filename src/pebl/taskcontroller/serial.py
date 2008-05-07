"""Module providing a taskcontroller than runs tasks serially."""

from pebl.taskcontroller.base import _BaseController

class SerialController(_BaseController):
    """A simple taskcontroller that runs tasks in serial in one process.

    This is just the default, null task controller.

    """

    def run(self, tasks):
        return [t.run() for t in tasks]
