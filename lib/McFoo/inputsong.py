import asynchat
import socket_pty
import McFoo.song
import string
import time

class InputSong(asynchat.async_chat):
    def __init__(self, playqueue):
	asynchat.async_chat.__init__(self, socket_pty.socket_pty())
	self.set_terminator('\n')
	self.command = ''
	self.last=None
        self.playqueue=playqueue
        self.last=time.time()

    def handle_connect(self):
	pass

    def ensure_connect(self):
	if not self.socket.connected:
	    self.connect(("/usr/lib/mc-foo/lib/pick-a-song", ["pick-a-song"]))
	
    def wakeup(self):
        self.ensure_connect()
        now=time.time()
        if now>self.last+1:
            self.ensure_connect()
            self.push("\n")
            self.last=now

    def collect_incoming_data(self, data):
	self.command = self.command + data

    def found_terminator(self):
	if self.command[-1]=='\015':
	    self.command = self.command[:-1]
	if self.command != '':
	    list = string.split(self.command, ' ', 2)
	    self.command = ''
            self.playqueue.add(McFoo.song.Song(list[0], list[1], list[2]))
