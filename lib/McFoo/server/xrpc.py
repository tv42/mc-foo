import xmlrpc
import McFoo.song

stop = 0

from errno import EADDRINUSE
class server(xmlrpc.server):
    def _methods(self):
        m = {}
        for name in dir(self.__class__):
            if name[:3] == 'do_':
                m['mcfoo.%s'%name[3:]]=getattr(self, name)
        return m
    
    def __init__(self, dj, playqueue):
        self.dj = dj
        self.playqueue = playqueue
        xmlrpc.server.__init__(self)
        self.addMethods(self._methods())

    def start_listen(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #TODO sock.set_reuse_addr()
	try:
	    sock.bind(("", 25706))
	    self.setFdAndListen(sock.fileno())
            self.socket=sock
	except socket.error, why:
	    if why[0] == EADDRINUSE:
	    	print "Address in use, not binding"
		sock.close()
	    else:
		raise socket.error, why

    def do_list(self, server, source, uri, name, args):
        print "got args: ", args
        serial=args[0]
        if serial==self.playqueue.serial:
            return {'serial': serial}
        else:
            return self.playqueue.as_data()

    def do_next(self, server, source, uri, name, args):
        server.dj.next()
        return []

    def do_pause(self, server, source, uri, name, args):
        server.dj.pause()
        return []

    def do_continue(self, server, source, uri, name, args):
        server.dj.play()
        return []

    def do_quit(self, server, source, uri, name, args):
        global stop
        stop = 1
        self.exit()
        return []

    def close(self):
        self.exit()
        return []

    def do_delete(self, server, source, uri, name, args):
        ok=[]
        for arg in args:
            try:
                self.playqueue.remove_by_id(arg)
                ok.append(arg)
            except IndexError:
                pass
        return ok

    def do_move(self, server, source, uri, name, args):
        for arg in args:
            id, offset = arg
            self.playqueue.move(id, offset)
        return []

    def do_moveabs(self, server, source, uri, name, args):
        for arg in args:
            id, newloc = arg
            self.playqueue.moveabs(id, newloc)
        return []

    def do_addqueue(self, server, source, uri, name, args):
        pri, backend, media, file=args[0], args[1], args[2], args[3]
        song=McFoo.song.Song(backend, media, file, pri)
        self.playqueue.add(song)
        return []

    def do_jump(self, server, source, uri, name, args):
        return []
