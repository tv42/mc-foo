import xmlrpc
import sys
import McFoo.song

stop = 0

from errno import EADDRINUSE, EINTR
class server(xmlrpc.server):
    def _methods(self):
        m = {}
        for name in dir(self.__class__):
            if name[:3] == 'do_':
                m['mcfoo.%s'%name[3:]]=getattr(self, name)
        return m
    
    def __init__(self, dj, playqueue, volume):
        self.dj = dj
        self.playqueue = playqueue
        self.volume = volume
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

    def do_pauseorplay(self, server, source, uri, name, args):
        server.dj.pauseorplay()
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
        for pri, backend, media, file in args:
            song=McFoo.song.Song(backend, media, file, pri)
            self.playqueue.add(song)
        return []

    def do_addqueueidx(self, server, source, uri, name, args):
        for pri, backend, media, file, idx in args:
            song=McFoo.song.Song(backend, media, file, pri)
            self.playqueue.insert(idx, song)
        return []

    def do_jump(self, server, source, uri, name, args):
        #TODO
        return []

    def do_volume_inc(self, server, source, uri, name, args):
        vol=None
        try:
            vol=args[0]
        except IndexError:
            pass
        self.volume.inc(vol)
        return []

    def do_volume_dec(self, server, source, uri, name, args):
        vol=None
        try:
            vol=args[0]
        except IndexError:
            pass
        self.volume.dec(vol)
        return []

    def do_volume_get(self, server, source, uri, name, args):
        return self.volume.get()

    def do_volume_set(self, server, source, uri, name, args):
        vol=args[0]
        self.volume.set(vol)
        return self.volume.get()

    def work(self, timeout=-1.0):
        try:
            xmlrpc.server.work(self, timeout)
        except:
            (type, value, traceback) = sys.exc_info()
            if type=="xmlrpc.error":
                (errno, strerror)=value
                if errno==EINTR:
                    pass
                else:
                    raise
            else:
                raise
