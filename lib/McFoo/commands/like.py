"""TODO"""

import McFoo.client
import sys, os.path
import twisted.internet.main
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] like" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientLike(j)
        c()

class McFooClientLike(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.like(pbcallback=twisted.internet.main.shutDown)
