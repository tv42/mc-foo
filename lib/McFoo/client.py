import twisted.internet.main
import twisted.spread.pb
import twisted.internet.tcp

import os

class McFooClientExitWhenDone(twisted.spread.pb.Referenced):
    def remote_done(self):
        twisted.internet.main.shutDown()

class McFooClientSimple:
    stopping = 0

    def __init__(self, user=None, password=None,
                 host=None, port=None):
        if user==None:
            user='guest'
        if password==None:
            password='guest'
        if host==None:
            try:
                host=os.environ['MCFOOHOST']
            except KeyError:
                host='localhost'
        if port==None:
            try:
                port=int(os.environ['MCFOOPORT'])
            except KeyError:
                port=25706

        self.remote = None
        broker = twisted.spread.pb.Broker()
        broker.requestPerspective('dj', user, password,
                                  self.handle_login,
                                  self.handle_loginfailure)
        broker.notifyOnDisconnect(self.handle_disconnect)
        self.tcp=twisted.internet.tcp.Client(host, port, broker)

    def handle_disconnect(self):
        if not self.stopping:
            print "Disconnected."
            twisted.internet.main.shutDown()

    def handle_loginfailure(self):
        print "Authentication failed."
        self.stopping = 1
        twisted.internet.main.shutDown()

    def handle_login(self, perspective):
        self.remote = perspective

    def __call__(self):
        twisted.internet.main.run()
