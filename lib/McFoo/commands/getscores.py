"""fetch your preferences from the server"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] getscores [USERNAME]" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, username="guest"):
        self.perspective=username

    def postOptions(self):
        c = McFooClientGetScores(self.perspective)
        c()

class McFooClientGetScores(McFoo.client.McFooClientSimple):
    def gotScores(self, scores):
        print scores
        self.stop()

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("getScores").addCallback(self.gotScores)
