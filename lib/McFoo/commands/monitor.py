"""monitor a dj server"""

import McFoo.client
import sys, os.path
from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: %s [options] monitor" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        c = McFooClientMonitorPlaying()
        c()


import McFoo.client
import McFoo.gui.song
import McFoo.volume
import McFoo.playqueue

class VolumeObserverMonitor(McFoo.volume.VolumeObserver):
    def __init__(self):
        McFoo.volume.VolumeObserver.__init__(self)

    def remote_change(self, left, right):
        x=((left+right)/2)
        print "Volume:", x
        sys.stdout.flush()

class HistoryObserverMonitor(McFoo.playqueue.HistoryObserver):
    def __init__(self):
        McFoo.playqueue.HistoryObserver.__init__(self)

    def remote_snapshot(self, history):
        try:
            h=history[-1]
        except IndexError:
            pass
        else:
            print McFoo.gui.song.GuiSong(h)
            sys.stdout.flush()

    def remote_add(self, song):
        print McFoo.gui.song.GuiSong(song)
        sys.stdout.flush()

class McFooClientMonitorPlaying(McFoo.client.McFooClientSimple):
    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        self.remote.callRemote("observe_volume", VolumeObserverMonitor())
        self.remote.callRemote("observe_history", HistoryObserverMonitor())
