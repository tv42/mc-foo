"""delete songs from the playqueue by song id"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] delete ID.." % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, *ids):
        ids=map(lambda x: int(x), ids)
        self.ids = ids

    def postOptions(self):
        if not self.ids:
            raise usage.UsageError, ("delete: no ids specified")
        c = McFooClientDelete(self.ids)
        c()

class McFooClientDelete(McFoo.client.McFooClientSimple):
    def __init__(self, ids):
        McFoo.client.McFooClientSimple.__init__(self)
        self.ids=ids

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("delete", self.ids).addCallback(reactor.stop)
