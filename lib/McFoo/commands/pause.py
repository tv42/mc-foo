"""send a pause command to dj"""

import McFoo.client
import sys, os.path
import twisted.internet.main
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] pause" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientPause()
        c()

class McFooClientPause(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.pause(pbcallback=twisted.internet.main.shutDown)
