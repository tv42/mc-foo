"""decrease the volume"""

import McFoo.client
import sys, os.path
import twisted.internet.main
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] vol-dec" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientVolume_dec()
        c()

class McFooClientVolume_dec(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.volume_dec(pbcallback=twisted.internet.main.shutDown)
