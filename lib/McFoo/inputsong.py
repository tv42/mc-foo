import McFoo.song
import string
import time
import twisted.internet.process
import twisted.protocols.protocol
import twisted.protocols.basic

class InputSong(twisted.internet.process.Process,
                twisted.protocols.basic.LineReceiver):
    delimiter = '\n'

    def __init__(self, playqueue, callback=None):
        twisted.internet.process.Process.__init__(self, "/usr/lib/mc-foo/lib/pick-a-song", ["pick-a-song"], {})
        self.playqueue=playqueue
        self.last=0
        self.callback=callback

        self.playqueue.filler=self.wakeup

    def handleChunk(self, chunk):
        self.dataReceived(chunk)

    def lineReceived(self, line):
	if line != '':
	    list = string.split(line, ' ', 2)
            self.playqueue.add(McFoo.song.Song(list[0], list[1], list[2]))
        if self.callback:
            self.callback()

    def startReading(self):
        twisted.internet.process.Process.startReading(self)
        self.transport=self.writer
        self.wakeup()

    def wakeup(self):
        now=time.time()
        if now>self.last+1 and self.transport:
            self.sendLine('')
            self.last=now


    def __getstate__(self):
        return {'playqueue': self.playqueue,
                'last': self.last,
                'callback': self.callback}

    def __setstate__(self, state):
        self.__init__(state['playqueue'], state['callback'])
        self.last=state['last']
