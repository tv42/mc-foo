import os
import sys
import string

import McFoo.backend.file
import McFoo.observe

from errno import EIO

import twisted.internet.process
import twisted.protocols.basic
import McFoo.observe

class DjObserver(McFoo.observe.Observer):
    def remote_change(self, at):
        pass

class Dj(twisted.internet.process.Process,
         twisted.protocols.basic.LineReceiver):
    delimiter = '\n'

    def __init__(self, playqueue):
        self.playqueue=playqueue

        self.player_state=None
        self.player_songlength=None
        self.player_at=None
        self.observers=McFoo.observe.Observers()

        self.missing_a_song=1

        twisted.internet.process.Process.__init__(self, "/usr/lib/mc-foo/lib/turntable", ["turntable"], {}, None)


    def __getstate__(self):
        return {'playqueue':self.playqueue}

    def __setstate__(self, state):
        self.__init__(state['playqueue'])

    def startReading(self):
        twisted.internet.process.Process.startReading(self)
        self.transport=self.writer
        self.ensure_music()

    def handleChunk(self, chunk):
        self.dataReceived(chunk)

    def ensure_music(self):
        if (self.missing_a_song
            and (self.player_state==None
                 or self.player_state=='waiting'
                 or self.player_state=='waiting_paused')):
            self.start_next_song()

    def start_next_song(self):
        next=self.playqueue.pop()
        if next:
            self.write("play %s\n"%next.filename)
            self.missing_a_song=0

    def lineReceived(self, line):
	if line != '':
	    list = string.split(line, ' ', 2)
            cmd=list[0]
            args=list[1:]
            if args:
                args=args[0]
            try:
                func=getattr(self, 'do_'+cmd)
            except AttributeError:
                print "dj: turntable said:", line
                pass
            else:
                func(args)
	    self.command = ''

    def do_state(self, args):
        self.player_state=args
        if self.player_state=='waiting':
            self.missing_a_song=1
        self.ensure_music()

    def do_length(self, args):
        self.player_songlength=float(args)

    def do_at(self, args):
        self.player_at=float(args)
        if self.player_songlength:
            at=self.player_at/self.player_songlength
            self.observers('change', at)
        else:
            self.observers('change', 0.0)

    def next(self):
        self.start_next_song()
        
    def pause(self):
        self.write("pause\n")

    def play(self):
        self.write("continue\n")

    def pauseorplay(self):
        self.write("toggle_pause\n")

    def jumpto(self, to):
        if self.player_songlength:
            to=to*self.player_songlength
            self.write("jumpto %f\n"%to)
        else:
            # no, you can't jump around in this song
            self.observers('change', 0.0)

    def jump(self, secs):
        if self.player_songlength:
            self.write("jump %f\n"%secs)
        else:
            # no, you can't jump around in this song
            self.observers('change', 0.0)

    def observe(self, callback):
        if self.player_songlength:
            at=((self.player_at or 0.0)
                /self.player_songlength)
        else:
            at=0.0
        self.observers.append_and_call(callback,
                                       'change',
                                       at)

    def unobserve(self, callback):
        self.observers.remove(callback)

    def handleError(self, text):
        print "turntable:", text,
