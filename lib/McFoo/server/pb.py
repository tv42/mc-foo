import re
import McFoo.song

stop = 0

from errno import EADDRINUSE, EINTR

from twisted.spread import pb
from twisted.python import log
from twisted.internet import reactor

def maybeTraceback(tb):
    if tb!=pb.PB_CONNECTION_LOST:
        pb.printTraceback(tb)

class CallMeLater:
    def __init__(self, callback, *a, **kw):
        self.callback=callback
        self.a=a
        self.kw=kw

    def __call__(self):
        return apply(self.callback, self.a, self.kw)

class DjPerspective(pb.Perspective):
    def __init__(self, perspectiveName, identityName, dj, playqueue, volume, profileTable):
        pb.Perspective.__init__(self, perspectiveName, identityName)
        self.dj = dj
        self.playqueue = playqueue
        self.volume = volume
        self.profileTable = profileTable
        self.onDetach = []

    def perspective_like(self):
        user=self.profileTable.adduser(self.identityName)
        user.incScore(self.playqueue.history[0].filename)

    def perspective_dislike(self):
        user=self.profileTable.adduser(self.identityName)
        user.incScore(self.playqueue.history[0].filename, -1)

    def perspective_hate(self):
        user=self.profileTable.adduser(self.identityName)
        user.incScore(self.playqueue.history[0].filename, -100)

    def perspective_getReadProfiles(self):
        user=self.profileTable.adduser(self.identityName)
        return user.def_read

    def perspective_setReadProfiles(self, l):
        user=self.profileTable.adduser(self.identityName)
        user.def_read=list(l)

    def perspective_getWriteProfiles(self):
        user=self.profileTable.adduser(self.identityName)
        return user.def_write

    def perspective_setWriteProfiles(self, l):
        user=self.profileTable.adduser(self.identityName)
        user.def_write=list(l)

    def perspective_getScores(self):
        user=self.profileTable.adduser(self.identityName)
        return user.as_data()

    def perspective_setScores(self, d):
        raise NotImplementedError #TODO

    def perspective_setscores(self, newScores):
        user=self.profileTable.adduser(self.identityName)
        return user.update(newScores)

    def perspective_list(self):
        return self.playqueue.as_data()

    def perspective_grep(self, regexp, ignorecase=0, invertmatch=0):
        flags = 0
        if ignorecase:
            flags = flags|re.IGNORECASE
        reg = re.compile(regexp, flags)
        l=[]
        for song in self.playqueue:
            if song.playable():
                if song.matchRegExp(reg) ^ invertmatch:
                    l.append(song.as_data())
        return l

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
        reactor.stop()

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

    def perspective_moveabs(self, newloc, ids):
        for id in ids:
            self.playqueue.moveabs(id, newloc)

    def perspective_addqueue(self, filename, priority=1000):
        song=McFoo.song.Song(filename, priority)
        self.playqueue.add(song)

    def perspective_addqueueidx(self, idx, songs):
        for pri, filename in songs:
            song=McFoo.song.Song(filename, pri)
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
        self.onDetach.append(CallMeLater(self.volume.unobserve, callback))

    def perspective_observe_location(self, callback):
        self.dj.observe(callback)
        self.onDetach.append(CallMeLater(self.dj.unobserve, callback))
        
    def perspective_observe_playqueue(self, callback):
        self.playqueue.observe(callback)
        self.onDetach.append(CallMeLater(self.playqueue.unobserve, callback))

    def perspective_observe_history(self, callback):
        self.playqueue.history.observe(callback)
        self.onDetach.append(CallMeLater(self.playqueue.history.unobserve, callback))

    def detached(self, reference, identity):
        log.msg('user %s detached' % identity.name)
        for f in self.onDetach:
            f()
        self.onDetach=[]

    def attached(self, reference, identity):
        log.msg('user %s attached' % identity.name)
        return self
