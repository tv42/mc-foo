import os
import sys
import string

import asynchat
import socket_pty

import McFoo.backend.file

class Dj(asynchat.async_chat):
    def __init__(self, playqueue):
	asynchat.async_chat.__init__(self, socket_pty.socket_pty())
	self.set_terminator('\n')
	self.command = ''
        self.playqueue=playqueue

        self.player_state=None
        self.player_songlength=None
        self.player_at=None

        self.ensure_connect()
        self.missing_a_song=1

    def ensure_music(self):
        if (self.missing_a_song
            and (self.player_state==None
                 or self.player_state=='waiting'
                 or self.player_state=='waiting_paused')):
            self.start_next_song()

    def start_next_song(self):
        next=self.playqueue.pop()
        if next:
            self.send("play %s\n"%next.filename)
            self.missing_a_song=0

    def handle_connect(self):
	pass

    def log(self, message):
        sys.stderr.write("dj log: "+message+"\n")

    def ensure_connect(self):
	if not self.socket.connected:
	    self.connect(("/usr/lib/mc-foo/lib/turntable", ["turntable"]))
	
    def collect_incoming_data(self, data):
	self.command = self.command + data

    def found_terminator(self):
	if self.command[-1]=='\015':
	    self.command = self.command[:-1]
	if self.command != '':
	    list = string.split(self.command, ' ', 2)
            cmd=list[0]
            args=list[1:]
            if args:
                args=args[0]
            try:
                func=getattr(self, 'do_'+cmd)
            except AttributeError:
                print "dj: turntable said:", self.command
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
        self.player_at=args

    def next(self):
        self.start_next_song()
        
    def pause(self):
        self.send("pause\n")

    def play(self):
        self.send("continue\n")

    def pauseorplay(self):
        self.send("toggle_pause\n")

    def fileno(self):
        self.ensure_connect()
        return self.socket.fileno()
