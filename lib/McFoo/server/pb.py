import sys
import McFoo.song

stop = 0

from errno import EADDRINUSE, EINTR

from twisted.spread import pb
import twisted.internet.main

def maybeTraceback(tb):
    if tb!=pb.PB_CONNECTION_LOST:
        pb.printTraceback(tb)

class DjPerspective(pb.Perspective):
    def __init__(self, perspectiveName, service, identityName, dj, playqueue, volume):
        pb.Perspective.__init__(self, perspectiveName, service, identityName)
        self.dj = dj
        self.playqueue = playqueue
        self.volume = volume

    def perspective_list(self):
        return self.playqueue.as_data()

    def perspective_next(self):
        self.dj.next()

    def perspective_pause(self):
        self.dj.pause()

    def perspective_pauseorplay(self):
        self.dj.pauseorplay()

    def perspective_cont(self):
        self.dj.play()

    def perspective_quit(self):
        global stop
        stop = 1
        twisted.internet.main.shutDown()

    def perspective_delete(self, args):
        for arg in args:
            try:
                self.playqueue.remove_by_id(arg)
            except IndexError:
                pass

    def perspective_move(self, args):
        for arg in args:
            id, offset = arg
            self.playqueue.move(id, offset)

    def perspective_moveabs(self, args):
        for arg in args:
            id, newloc = arg
            self.playqueue.moveabs(id, newloc)

    def perspective_addqueue(self, pri, backend, media, file):
        song=McFoo.song.Song(backend, media, file, pri)
        self.playqueue.add(song)

    def perspective_addqueueidx(self, args):
        for pri, backend, media, file, idx in args:
            song=McFoo.song.Song(backend, media, file, pri)
            self.playqueue.insert(idx, song)

    def perspective_jumpto(self, args):
        self.dj.jumpto(args)
        pass

    def perspective_jump(self, args):
        self.dj.jump(args)
        pass

    def perspective_volume_inc(self, delta=None):
        self.volume.inc(delta)

    def perspective_volume_dec(self, delta=None):
        self.volume.dec(delta)

    def perspective_volume_get(self, args):
        return self.volume.get()

    def perspective_volume_set(self, vol_left, vol_right=None):
        self.volume.set(vol_left, vol_right)
        return self.volume.get()

    def perspective_observe_volume(self, callback):
        self.volume.observe(callback)
        
    def perspective_observe_location(self, callback):
        self.dj.observe(callback)
        
    def perspective_observe_playqueue(self, callback):
        self.playqueue.observe(callback)

    def perspective_observe_history(self, callback):
        self.playqueue.history.observe(callback)


class server(pb.Service):
    def __init__(self, app, dj, playqueue, volume):
        pb.Service.__init__(self, "dj", app)
        self.dj = dj
        self.playqueue = playqueue
        self.volume = volume

    def getPerspectiveNamed(self, name):
        return DjPerspective(name, self, "Nobody", self.dj, self.playqueue, self.volume)
