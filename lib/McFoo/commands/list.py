"""show dj's playqueue"""

import McFoo.client
import sys, os.path
import twisted.internet.main
from twisted.python import usage
from errno import EPIPE

class Options(usage.Options):
    synopsis = "Usage: %s [options] list" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientList()
        c()

def ShowList(l):
    for s in l:
        if s.has_key('id') and s.has_key('filename'):
            print "%-3d %s" % (s['id'], s['filename'])
    twisted.internet.main.shutDown()

class McFooClientList(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.list(pbcallback=ShowList)
