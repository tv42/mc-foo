import ao
import os
import string
import select
import sys
import time

import asyncore
import asyncreadline

import McFoo.backend.file

states = {
    'playing': {
    'pause': 'paused',
    'continue': 'playing',
    'toggle_pause': 'paused',
    'got_song': 'playing',
    'song_end': 'waiting',
    },

    'paused': {
    'pause': 'paused',
    'continue': 'playing',
    'toggle_pause': 'playing',
    'got_song': 'playing',
    },

    'waiting': {
    'pause': 'waiting_paused',
    'continue': 'waiting',
    'toggle_pause': 'waiting_paused',
    'got_song': 'playing',
    },

    'waiting_paused': {
    'pause': 'waiting_paused',
    'continue': 'waiting_paused',
    'toggle_pause': 'waiting',
    'got_song': 'paused',
    },
}

class fdsocket:
    def __init__(self, fd):
        self.fd=fd

    def recv(self, buffer_size):
        return os.read(self.fd, buffer_size)

    def send(self, data):
        assert self.fd>=0
        return os.write(self.fd, data)

    def fileno(self):
        return self.fd

    def close(self):
        r=os.close(self.fd)
        self.fd=-1
        return r

    def setblocking(self, block):
        return 1

    def getpeername(self):
        return None

class TurntableInput(asyncreadline.asyncreadline):
    def __init__(self, callback, conn=None):
        asyncreadline.asyncreadline.__init__(self, conn)
        self.callback=callback

    def handle_connect(self):
	pass

    def ensure_connect(self):
        pass

    def writable(self):
        return 0

    def handle_write(self):
        raise "handle_read on a read-only fd"

    def process(self, line):
	if line and line[-1]=='\015':
	    line = line[:-1]
	if line != '':
            args = string.split(line, ' ', 1)

            cmd=args[0]
            args=args[1:]
            if args:
                args=args[0]
            self.callback(cmd, args)

    def log(self, message):
        sys.stderr.write("turntable reader log: "+message+"\n")

class TurntableStatus(asyncore.dispatcher_with_send):
    last=0
    was_at=None

    def state(self, state):
        print ("state_transition -> %s"%state)
        self.send('state %s\n'%state)

    def at(self, at):
        if (self.out_buffer==''
            and time.time()>self.last+1
            and at!=self.was_at):
            self.send("at %s\n"%at)
            self.last=time.time()
            self.was_at=at

    def handle_connect(self):
	pass

    def readable(self):
        return 0

    def handle_read(self):
        raise "handle_read on a write-only fd"

    def ensure_connect(self):
        pass

    def log(self, message):
        sys.stderr.write("turntable writer log: "+message+"\n")

class Turntable:
    def __init__(self):
        self._audio_dev = ao.AudioDevice('oss')
        self.file=None
        self._command=None
        self.state='waiting'
        self.input=TurntableInput(self.process, fdsocket(sys.stdin.fileno()))
        self.status=TurntableStatus(fdsocket(sys.stdout.fileno()))

    def process(self, cmd, args):
        if cmd=='play' and args:
            try:
                print "opening file %s"%args
                self.file=McFoo.backend.file.audiofilechooser(args)
            except McFoo.backend.file.McFooBackendFileUnknownFormat:
                print "unknown format"
                self.file=None
            else:
                print "old state: %s"%self.state
                self.state=states[self.state]['got_song']
                print "new state: %s"%self.state
                self.file.start_play()
                self.status.state(self.state)
                self.status.send("length %s\n"%self.file.time_total())
        elif cmd in ['pause', 'continue', 'toggle_pause'] and not args:
            self.state=states[self.state][cmd]
            self.status.state(self.state)
        elif cmd=='jump' and args:
            self.jumpto(self.file.time_tell()+float(args))
        elif cmd=='jumpto' and args:
            self.jumpto(float(args))
        else:
            print "bad command", cmd

    def poll_timeout(self):
        if self.state=='playing':
            return 0 # don't block
        else:
            return 1.0 # block for all playing cares of

    def loop(self):
        while self.input.socket.fd>=0:
            asyncore.poll(self.poll_timeout())
            if self.state=='playing':
                if self.file==None:
                    raise "why is file None?"
                self.status.at(self.file.time_tell())
                self.play()

    def play(self):
        SIZE = 4096

        (buff, bytes, bit) = self.file.read(SIZE)
        if bytes == 0:
            self.state=states[self.state]['song_end']
            self.status.state(self.state)
            self.file=None
            return
        self._audio_dev.play(buff, bytes)

    def jumpto(self, to):
        total=self.file.time_total()
        if to > total:
            to=total
        if to < 0:
            to=0
        self.file.time_seek(to)
