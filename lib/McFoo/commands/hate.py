"""record that you think this song is good"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] hate [USERNAME]" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, username="guest"):
        self.perspective=username

    def postOptions(self):
        c = McFooClientHate(self.perspective)
        c()

class McFooClientHate(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("hate").addCallback(self.stop)
