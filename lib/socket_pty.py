import os
class socket_pty:
    def __init__(self):
	self.connected=0
	self.fd=None
	self.nonblock=0

    def setblocking(self, bool=None):
	if bool!=None:
	    self.nonblock=bool
	else:
	    bool=self.nonblock
	if self.fd!=None:
	    import fcntl
	    import FCNTL
	    flags = fcntl.fcntl(self.fd, FCNTL.F_GETFL, 0)
	    if bool:
		flags = flags | FCNTL.O_NONBLOCK
	    else:
		flags = flags & ~FCNTL.O_NONBLOCK
		fcntl.fcntl (self.fd, FCNTL.F_SETFL, flags)

    def setsockopt(self, *foo):
	raise "not a socket"

    def getsockopt(self, *foo):
	raise "not a socket"

    def listen(self, num):
	raise "not a socket"
    
    def bind(self, addr):
	raise "not a socket"

    def connect(self, cmd):
	import pty
	self.close()
	pid, fd = pty.fork()
	if pid==0:
	    # child
	    os.execv(cmd)
	else:
	    # parent
	    self.fd=fd
	    self.setblocking()
	    self.connected=1

    def accept(self, addr):
	raise "not a socket"

    def send(self, data):
	return os.write(self.fd, data)

    def recv(self, buffer_size):
	return os.read(self.fd, buffer_size)

    def close(self):
	if self.fd!=None:
	    os.close(self.fd)

    def fileno(self):
	return self.fd
