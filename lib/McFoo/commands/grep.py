"""show dj's playqueue"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage
from errno import EPIPE

class Options(usage.Options):
    synopsis = "Usage: %s [options] grep [OPTIONS] REGEXP" % os.path.basename(sys.argv[0])
    optFlags = [['ignore-case', 'i'], ['invert-match', 'v']]

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, regexp):
        self.regexp=regexp

    def postOptions(self):
        c = McFooClientGrep(self.regexp,
                            ignorecase=self['ignore-case'],
                            invertmatch=self['invert-match'],
                            )
        c()

def ShowList(l):
    for s in l:
        if s.has_key('id') and s.has_key('filename'):
            print "%-3d %s" % (s['id'], s['filename'])
    reactor.stop()

class McFooClientGrep(McFoo.client.McFooClientSimple):
    def __init__(self, regexp, ignorecase, invertmatch):
        self.regexp=regexp
        self.ignorecase=ignorecase
        self.invertmatch=invertmatch
        McFoo.client.McFooClientSimple.__init__(self)

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("grep", self.regexp,
                               ignorecase=self.ignorecase,
                               invertmatch=self.invertmatch).addCallback(ShowList)
