import twisted.internet.main
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

        self.remote = None
        twisted.spread.pb.connect(
            McFoo.config.store.host,
            McFoo.config.store.port,
            user, password, "dj"
            ).addCallbacks(self.handle_connect,
                           self.handle_failure)


    def handle_failure(self, message):
        if not self.stopping:
            print "Cannot contact DJ:", message
            twisted.internet.main.shutDown()

    def handle_connect(self, perspective):
        perspective.broker.notifyOnDisconnect(self.handle_disconnect)
        self.remote = perspective
        self.handle_login(perspective)

    def handle_login(self, perspective):
        pass

    def handle_disconnect(self):
        pass

    def __call__(self):
        twisted.internet.main.run()
