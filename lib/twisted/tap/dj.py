
# Twisted, the Framework of Your Internet
# Copyright (C) 2001 Matthew W. Lefkowitz
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""
I am the support module for making a DJ server with mktap.
"""

from twisted.python import usage

class Options(usage.Options):
    synopsis = "Usage: mktap dj [options]"
    optStrings = [["dir", "d", "/data/music","path to search for songs"],
                  ]

    longdesc = "Makes a DJ server."

    def opt_port(self, opt):
        """set the port to listen on
        """
        try:
	    self.portno = int(opt)
	except ValueError:
	    raise usage.error("Invalid argument to 'port'!")
    opt_p = opt_port

def getPorts(app, config):
    ports = []

    profileTable=McFoo.score.ProfileTable()
    filler=McFoo.suggest.Suggestions(config.dir, profileTable)
    playqueue = McFoo.playqueue.PlayQueue(filler.get)
    dj = McFoo.dj.Dj(playqueue)
    volume = McFoo.volume.VolumeControl()

    service=McFoo.server.pb.server(app, dj, playqueue, volume, profileTable)
    perspective=service.getPerspectiveNamed("guest")
    perspective.setService(service)
    perspective.makeIdentity("guest")

    try:
        portno = config.portno
    except AttributeError:
        portno = 25706

    prot = pb.BrokerFactory(pb.AuthRoot(app))

    ports.append((int(portno), prot))
    return ports

###########################

from twisted.spread import pb

import McFoo.playqueue
import McFoo.dj
import McFoo.volume
import McFoo.server.pb
import McFoo.suggest
import McFoo.score
import select
import os

from twisted.internet import main

import dj
