"""send a skip to next song command to dj"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor, defer
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] next" % os.path.basename(sys.argv[0])
    optFlags = [['dislike', None], ['hate', None]]

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientNext(hate=self['hate'], dislike=self['dislike'])
        c()

class McFooClientNext(McFoo.client.McFooClientSimple):
    def __init__(self, hate=0, dislike=0):
        self.hate=hate
        self.dislike=dislike
        McFoo.client.McFooClientSimple.__init__(self)

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        if self.hate:
            d=self.remote.callRemote("hate")
        elif self.dislike:
            d=self.remote.callRemote("dislike")
        else:
            d=defer.succeed(None)
        d.addCallback(self._next)

    def _next(self, dummy):
        self.remote.callRemote("next").addCallback(self.stop)
