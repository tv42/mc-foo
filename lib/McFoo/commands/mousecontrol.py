"""control dj with a mouse (raw, no GPM, no X)"""

# left: pause/continue
# middle: next
# middle+drag left right: rew/ff (TODO)
# right+drag up down: volume
# right: mute (TODO)

import McFoo.client
import sys, os, os.path
from twisted.internet import reactor
from twisted.python import usage
try:
    from twisted.protocols.mice.mouseman import MouseMan
except ImportError:
    # use a dummy until a Twisted version with the support is available
    class MouseMan:
        FAKE=1

from twisted.internet import protocol, abstract

class SerialPort(abstract.FileDescriptor):
    def __init__(self, filename):
        self.fd = os.open(filename, os.O_RDONLY)

    def fileno(self):
        return self.fd

    def doRead(self):
        # TODO move this back out as soon as such versio of Twisted is
        # packaged.
        from twisted.internet import fdesc
        return fdesc.readFromFD(self.fileno(), self.protocol.dataReceived)

class Options(usage.Options):
    synopsis = "Usage: %s [options] mousecontrol [--file=FILE]" % os.path.basename(sys.argv[0])
    optParameters = [['file', 'f', '/dev/tts/0']]

    def __init__(self):
        usage.Options.__init__(self)
        
    def postOptions(self):
        if hasattr(MouseMan, 'FAKE'):
            raise "Your twisted is too old to contain twisted.protocols.mice"
        c = McFooClientMouseControl()
        transport = SerialPort(self.opts['file'])
        transport.protocol = McFooMouse(c)
        reactor.addReader(transport)
        c()

class McFooClientMouseControl(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)

    def handle_disconnect(self):
        self.connect()

class McFooMouse(MouseMan):
    def __init__(self, client):
        self.client = client

    def down_left(self):
        if self.client.remote:
            self.client.remote.callRemote("pauseorplay")

    def down_middle(self):
        if self.client.remote:
            self.client.remote.callRemote("next")

    def move(self, x, y):
        if self.client.remote and self.rightbutton:
            self.client.remote.callRemote("volume_inc", delta=-y)
