"""send a continue paused song command to dj"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] continue" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientContinue()
        c()

class McFooClientContinue(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("cont").addCallback(reactor.stop)
