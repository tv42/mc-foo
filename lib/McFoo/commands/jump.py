"""rewind or fast forward within the song"""

import McFoo.client
import sys, os.path
import twisted.internet.main
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] jump JUMPTO" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, jumpto):
        self.jumpto=float(jumpto)

    def postOptions(self):
        c = McFooClientJump(self.jumpto)
        c()

class McFooClientJump(McFoo.client.McFooClientSimple):
    def __init__(self, jump):
        McFoo.client.McFooClientSimple.__init__(self)
        self.jump=jump

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("jump", self.jump).addCallback(twisted.internet.main.shutDown)
