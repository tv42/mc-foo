import os

from errno import EIO

class socket_pty:
    def __init__(self):
	self.fd=None
	self.nonblock=0

    def __getattr__(self, name):
        if name=='connected':
            return self.fd!=None
        else:
            raise AttributeError, name

    def setblocking(self, bool):
        self.nonblock=bool
        if self.fd!=None:
            self.refresh_nonblocking()

    def refresh_nonblocking(self):
        if self.fd==None:
            raise 'fd still None'
        import fcntl
        import FCNTL
        flags = fcntl.fcntl(self.fd, FCNTL.F_GETFL, 0)
        if self.nonblock:
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
        if self.fd!=None:
            self.close()
	pid, fd = pty.fork()
	if pid==0:
	    # child
	    apply(os.execv, cmd)
	else:
	    # parent
	    self.fd=fd
            self.refresh_nonblocking()

    def accept(self, addr):
	raise "not a socket"

    def send(self, data):
        if self.fd==None:
            raise 'fd still None'
	return os.write(self.fd, data)

    def recv(self, buffer_size):
        if self.fd==None:
            raise 'fd still None'
        try:
            return os.read(self.fd, buffer_size)
        except OSError, e:
            if e==EIO:
                self.fd=None
                return ''
            else:
                print "socket_pty.recv: e="%`e`
                raise

    def close(self):
        if self.fd==None:
            raise 'fd still None'
        os.close(self.fd)
        self.fd=None

    def fileno(self):
        if self.fd==None:
            raise 'fd still None'
	return self.fd
