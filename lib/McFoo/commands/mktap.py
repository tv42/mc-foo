"""make a twisted tap file"""

import sys, os.path
from twisted.internet import main
from twisted.python import usage
from twisted.spread import pb
import McFoo.playqueue
import McFoo.dj
import McFoo.volume
import McFoo.server.pb
import McFoo.suggest
import McFoo.score

class Options(usage.Options):
    synopsis = "Usage: %s [options] jump JUMPTO" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def parseArgs(self, songdir):
        self.songdir=songdir

    def postOptions(self):
        #import dj

        profileTable=McFoo.score.ProfileTable()
        filler=McFoo.suggest.Suggestions(self.songdir, profileTable)
        playqueue = McFoo.playqueue.PlayQueue(filler.get)
        dj = McFoo.dj.Dj(playqueue)
        volume = McFoo.volume.VolumeControl()

        app = main.Application("dj")
        service=McFoo.server.pb.server(app, dj, playqueue, volume, profileTable)
        perspective=service.getPerspectiveNamed("guest")
        perspective.setService(service)
        perspective.makeIdentity("guest")

        port=25706
        
        app.listenOn(port, pb.BrokerFactory(pb.AuthRoot(app)))
        
        app.save("start")
