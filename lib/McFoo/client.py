from twisted.internet import reactor
import twisted.spread.pb
import McFoo.config

import os

class McFooClientSimple:
    stopping = 0

    def __init__(self, user=None, password=None,
                 host=None, port=None):
        if user==None:
            user='guest'
        if password==None:
            password='guest'

        self.user=user
        self.password=password
        self.remote = None
        self.connect()

    def connect(self):
        twisted.spread.pb.connect(
            McFoo.config.store.host,
            McFoo.config.store.port,
            self.user, self.password, "dj"
            ).addCallbacks(self.handle_connect,
                           self.handle_failure)

    def handle_failure(self, message):
        if not self.stopping:
            print "Cannot contact DJ:", message
            reactor.stop()

    def handle_connect(self, perspective):
        perspective.broker.notifyOnDisconnect(self.handle_disconnect)
        self.remote = perspective
        self.handle_login(perspective)

    def handle_login(self, perspective):
        pass

    def handle_disconnect(self):
        pass

    def __call__(self):
        reactor.run()

    def stop(self, *foo, **bar):
        # you can give me extra args and I won't mind.
        # useful for pb callbacks.
        reactor.stop()
