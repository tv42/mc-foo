"""fetch your preferences from the server"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] getwriteprofiles [USERNAME]" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, username="guest"):
        self.perspective=username

    def postOptions(self):
        c = McFooClientGetWriteProfiles(self.perspective)
        c()

class McFooClientGetWriteProfiles(McFoo.client.McFooClientSimple):
    def gotProfiles(self, profiles):
        print ' '.join(profiles)
        self.stop()

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("getWriteProfiles").addCallback(self.gotProfiles)
