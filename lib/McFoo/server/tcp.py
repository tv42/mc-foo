import asynchat
import asyncmd
import McFoo.dj

from errno import EADDRINUSE
class server(asynchat.async_chat, asyncmd.async_cmd):
    def __init__(self, dj):
        asynchat.async_chat.__init__(self)
        self.set_terminator('\n')
        self.command = ''
        self.dj = dj

    def start_listen(self):
        import socket
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
	try:
	    self.bind(("", 25706))
	    self.listen(5)
	except socket.error, why:
	    if why[0] == EADDRINUSE:
	    	print "Address in use, not binding"
		self.close()
	    else:
		raise socket.error, why

    def collect_incoming_data(self, data):
        self.command = self.command + data

    def found_terminator(self):
        print "client=%d command=%s" % (self.fileno(), self.command)
        self.onecmd(self.command)
        self.command = ''

    def do_next(self, arg):
        self.dj.next()
        self.push("COMMAND: next\n")

    def do_quit(self, arg):
	# TODO make it _all_ go away
        self.push("THEEND (not yet)\n")
        self.close_when_done()

    def do_list(self, arg):
	self.push("MULTI foo\n"+str(playqueue))

    def do_dump(self, arg):
        self.push(repr(playqueue)+"\n")

    def do_pause(self, arg):
        self.dj.pause()
        self.push("COMMAND: pause\n")

    def do_continue(self, arg):
        self.dj.play()
        self.push("COMMAND: continue\n")

    def do_delete(self, arg):
	from string import strip
	arg=int(arg)
	songs=filter(lambda x: x.id==arg, playqueue)
	if songs==[]:
	    self.push("COMMAND: remove %d failed\n" % arg)
	else:
	    for song in songs:
		playqueue.remove(song)
		self.push("COMMAND: remove %s\n" % song.filename)

    def do_move(self, arg):
        pass

    def do_addqueue(self, arg):
        pass

    def do_jump(self, arg):
        pass

    def handle_accept(self):
        (conn, addr) = self.accept()
        s = server(self.dj)
        s.set_socket(conn)

    def handle_connect(self):
        pass

    def say(self, string):
        self.push(string+"\n")

    def raw_input(self, prompt):
        if prompt==None: prompt=">>> "
        self.push(prompt)
        raise
    	#TODO
