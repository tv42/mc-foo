"""increase the volume"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] vol-inc" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientVolume_inc()
        c()

class McFooClientVolume_inc(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("volume_inc").addCallback(self.stop)
