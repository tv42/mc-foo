"""an interface to dj"""

import McFoo.client
import sys, os.path
from twisted.python import usage
from Tkinter import *

class Options(usage.Options):
    synopsis = "Usage: %s [options] fan" % os.path.basename(sys.argv[0])

    def __init__(self):
        usage.Options.__init__(self)

    def postOptions(self):
        main()

class McFooClientFan(McFoo.client.McFooClientSimple):
    def __init__(self, TkRoot=None, user=None, password=None,
                 host=None, port=None):
        McFoo.client.McFooClientSimple.__init__(self,
                                                user, password,
                                                host, port)
        self.root=TkRoot

    def handle_login(self, perspective):
        McFoo.client.McFooClientSimple.handle_login(self, perspective)
        pq = McFoo.gui.playqueue.PlayQueue(self.root, self.remote)
        
        pq.history.listbox.config(selectmode=EXTENDED)
        pq.queue.listbox.config(selectmode=EXTENDED)
        self.root.deiconify()

    def handle_failure(self, message):
        McFoo.client.McFooClientSimple.handle_failure(self, message)
        self.root.quit()

    def handle_disconnect(self):
        McFoo.client.McFooClientSimple.handle_disconnect(self)
        print "Disconnected."
        self.root.quit()

def main():
    import McFoo.gui.playqueue
    import os
    import twisted.internet.tksupport
    from twisted.internet import reactor
    root = Tk()
    root.withdraw()
    twisted.internet.tksupport.install(root)
    c = McFooClientFan(TkRoot=root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

    reactor.stop()
