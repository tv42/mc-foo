"""add a song to queue"""

import McFoo.client
import sys, os.path
from twisted.internet import reactor
from twisted.python import usage
from twisted.python.defer import DeferredList

class Options(usage.Options):
    synopsis = "Usage: %s [options] addqueue [--priority=N] FILENAME.." % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)
        self.pri=10

    def parseArgs(self, *filenames):
        if not filenames:
            self.opt_help()
            return
        self.filenames=filenames

    def postOptions(self):
        c = McFooClientAddqueue(self.pri, self.filenames)
        c()

    def opt_priority(self, pri):
        try:
            pri=int(pri)
        except ValueError:
            raise
        self.pri=pri

class McFooClientAddqueue(McFoo.client.McFooClientSimple):
    def __init__(self, pri, files):
        McFoo.client.McFooClientSimple.__init__(self)
        self.pri=pri
        self.files=files

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        deferreds = []
        for file in self.files:
            d = self.remote.callRemote("addqueue", file, self.pri)
            deferreds.append(d)
        dl = DeferredList(deferreds)
        dl.addCallback(self.stop)
        dl.arm()
