"""add a song to queue"""

import McFoo.client
import sys, os.path
import twisted.internet.main
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] addqueue PRIORITY FILENAME" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)
        self.pri=10

    def parseArgs(self, filename):
        self.filename=filename

    def postOptions(self):
        c = McFooClientAddqueue(self.pri, self.filename)
        c()

    def opt_priority(self, pri):
        try:
            pri=int(pri)
        except ValueError:
            raise
        self.pri=pri

class McFooClientAddqueue(McFoo.client.McFooClientSimple):
    def __init__(self, pri, file):
        McFoo.client.McFooClientSimple.__init__(self)
        self.pri=pri
        self.file=file

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.addqueue(self.file, self.pri,
                             pbcallback=twisted.internet.main.shutDown)
