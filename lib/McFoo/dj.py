import os
import sys
import string

import McFoo.backend.file
import McFoo.observe

from errno import EIO

import twisted.internet.process
from twisted.internet import protocol
import twisted.protocols.basic
from twisted.python import log
from twisted.spread import pb
from twisted.persisted import styles
from twisted.internet import reactor
import McFoo.observe
import McFoo.server.pb
import McFoo.audiodevice

class DjObserver(McFoo.observe.Observer):
    def remote_change(self, at):
        pass

class Dj(pb.Service):
    def __init__(self, app, playqueue, volume, profileTable):
        pb.Service.__init__(self, "dj", app)
        self.playqueue = playqueue
        self.volume = volume
        self.profileTable = profileTable

        self.observers=McFoo.observe.Observers()

        self._audio_dev = McFoo.audiodevice.AudioDevice()
        self.file=None

        self.timer=None
        self.next()

    def startService(self):
        if self.file:
            self.timer = reactor.callLater(0, self._tick)
        else:
            self.next()

    def pause(self):
        if self.timer:
            reactor.cancelCallLater(self.timer)
            self.timer=None

    def pauseorplay(self):
        if self.timer:
            self.pause()
        else:
            self.play()

    def getPerspectiveNamed(self, name):
        return McFoo.server.pb.DjPerspective(name, "Nobody", self, self.playqueue, self.volume, self.profileTable)
    delimiter = '\n'

    def next(self):
        self.file=None
        while 1:
            next=self.playqueue.pop()
            filename=next.filename
            try:
                self.file=McFoo.backend.file.audiofilechooser(filename)
            except McFoo.backend.file.McFooBackendFileUnknownFormat:
                print "unkown format:", next
                pass
            except McFoo.backend.file.McFooBackendFileDoesNotExist:
                print "file does not exist:", next
                pass
            else:
                break
            
        self.file.start_play()
        self.play()

    def play(self):
        if not self.timer:
            self.timer = reactor.callLater(0, self._tick)

    def _tick(self):
        self.timer = None

        SIZE = 8192

        (buff, bytes, bit) = self.file.read(SIZE)
        if bytes == 0:
            self.next()
        self._audio_dev.play(buff, bytes)
        self.timer = reactor.callLater(0, self._tick)

    def _jumpto(self, to):
        total=self.file.time_total()
        if to > total:
            to=total
        if to < 0:
            to=0
        self.file.time_seek(to)

    def jumpto(self, to):
        if self.file.time_total():
            to=to*self.file.time_total()
            self._jumpto(to)
        else:
            # no, you can't jump around in this song
            self.observers('change', 0.0)

    def jump(self, secs):
        if self.file.time_total():
            self._jumpto(self.file.time_tell()+float(secs))
        else:
            # no, you can't jump around in this song
            self.observers('change', 0.0)

    def observe(self, callback):
        if self.file.time_total():
            at=((self.file.time_tell() or 0.0)
                /self.file.time_total())
        else:
            at=0.0
        self.observers.append_and_call(callback,
                                       'change',
                                       at)

    def unobserve(self, callback):
        self.observers.remove(callback)
