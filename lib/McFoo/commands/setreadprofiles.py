"""fetch your preferences from the server"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] setreadprofiles [--user=USERNAME] PROFILE.." % os.path.basename(sys.argv[0])
    optParameters = [['user', 'u', 'guest']]

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, *profiles):
        self.profiles=profiles

    def postOptions(self):
        c = McFooClientSetReadProfiles(self['user'], self.profiles)
        c()

class McFooClientSetReadProfiles(McFoo.client.McFooClientSimple):
    def __init__(self, perspective, profiles):
        self.profiles=profiles
        McFoo.client.McFooClientSimple.__init__(self, perspective)

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("setReadProfiles", self.profiles).addCallback(self.stop)
