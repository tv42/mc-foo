"""record that you think this song is good"""

import McFoo.client
import sys, os.path
import twisted.internet.main
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] like [USERNAME]" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, username="guest"):
        self.perspective=username

    def postOptions(self):
        c = McFooClientLike(self.perspective)
        c()

class McFooClientLike(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("like").addCallback(twisted.internet.main.shutDown)
