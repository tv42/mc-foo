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
    def __init__(self, dj, playqueue, volume):
        self.dj = dj
        self.playqueue = playqueue
        self.volume = volume

    def perspective_list(self, callback=None):
        callback.done(self.playqueue.as_data(), pberrback=maybeTraceback)

    def perspective_next(self, callback=None):
        self.dj.next()
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_pause(self, callback=None):
        self.dj.pause()
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_pauseorplay(self, callback=None):
        self.dj.pauseorplay()
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_cont(self, callback=None):
        self.dj.play()
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_quit(self, callback=None):
        global stop
        stop = 1
        twisted.internet.main.shutDown()
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_delete(self, args, callback=None):
        for arg in args:
            try:
                self.playqueue.remove_by_id(arg)
            except IndexError:
                pass
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_move(self, args, callback=None):
        for arg in args:
            id, offset = arg
            self.playqueue.move(id, offset)
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_moveabs(self, args, callback=None):
        for arg in args:
            id, newloc = arg
            self.playqueue.moveabs(id, newloc)
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_addqueue(self, pri, backend, media, file, callback=None):
        song=McFoo.song.Song(backend, media, file, pri)
        self.playqueue.add(song)
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_addqueueidx(self, args, callback=None):
        for pri, backend, media, file, idx in args:
            song=McFoo.song.Song(backend, media, file, pri)
            self.playqueue.insert(idx, song)
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_jump(self, args, callback=None):
        #TODO
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_volume_inc(self, delta=None, callback=None):
        self.volume.inc(delta)
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_volume_dec(self, delta=None, callback=None):
        self.volume.dec(delta)
        if callback:
            callback.done(pberrback=maybeTraceback)

    def perspective_volume_get(self, args, callback=None):
        if callback:
            callback.done(self.volume.get(), pberrback=maybeTraceback)

    def perspective_volume_set(self, vol_left, vol_right=None, callback=None):
        self.volume.set(vol_left, vol_right)
        if callback:
            callback.done(self.volume.get(), pberrback=maybeTraceback)

    def perspective_observe_volume(self, callback):
        self.volume.observe(callback)
        
    def perspective_observe_playqueue(self, callback):
        self.playqueue.observe(callback)

    def perspective_observe_history(self, callback):
        self.playqueue.history.observe(callback)


class server(pb.Service):
    def __init__(self, dj, playqueue, volume):
        pb.Service.__init__(self)
        self.dj = dj
        self.playqueue = playqueue
        self.volume = volume

    def getPerspectiveNamed(self, name):
        return DjPerspective(self.dj, self.playqueue, self.volume)
