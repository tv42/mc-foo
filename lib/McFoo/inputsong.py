import asynchat
import socket_pty
import McFoo.song
import string

class InputSong(asynchat.async_chat):
    def __init__(self, playqueue):
	asynchat.async_chat.__init__(self, socket_pty.socket_pty())
	self.set_terminator('\n')
	self.command = ''
	self.last=None
        self.playqueue=playqueue
        self.outstanding=0

    def handle_connect(self):
	pass

    def ensure_connect(self):
	if not self.socket.connected:
	    self.connect(("/usr/lib/mc-foo/lib/pick-a-song", ["pick-a-song"]))
	
    def wakeup(self):
	self.ensure_connect()
        if not self.outstanding:
            self.outstanding=self.outstanding+1
	    self.push("\n")

    def collect_incoming_data(self, data):
	self.command = self.command + data

    def found_terminator(self):
	if self.command[-1]=='\015':
	    self.command = self.command[:-1]
	if self.command != '':
            self.outstanding=self.outstanding-1
	    list = string.split(self.command, ' ', 2)
	    self.command = ''
	    self.playqueue.add(McFoo.song.Song('/var/lib/mc-foo/media/%s/%s/path/%s' % (list[0], list[1], list[2])))
