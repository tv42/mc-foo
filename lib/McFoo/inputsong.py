import asyncreadline
import socket_pty
import McFoo.song
import string
import time

class InputSong(asyncreadline.asyncreadline):
    def __init__(self, playqueue):
	asyncreadline.asyncreadline.__init__(self, socket_pty.socket_pty())
        self.playqueue=playqueue
        self.last=0
        self.ensure_connect()

    def handle_connect(self):
	pass

    def ensure_connect(self):
	if not self.socket.connected:
	    self.connect(("/usr/lib/mc-foo/lib/pick-a-song", ["pick-a-song"]))
	
    def process(self, line):
	if line[-1]=='\015':
	    line = line[:-1]
	if line != '':
	    list = string.split(line, ' ', 2)
            self.playqueue.add(McFoo.song.Song(list[0], list[1], list[2]))

    def wakeup(self):
        self.ensure_connect()
        now=time.time()
        if now>self.last+1:
            self.ensure_connect()
            self.push("\n")
            self.last=now

