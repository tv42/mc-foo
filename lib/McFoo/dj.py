import McFoo.backend.file
class Dj:
    def _player(self):
        while 1:
            self._playable.wait()
            self._playfile(self._song.filename)
            self._song=None
            self._playable.clear()

    def __init__(self):
        import ao
        from threading import Thread, Event
        self._audio_id = ao.get_driver_id('oss')
        self._audio_dev = ao.AudioDevice(self._audio_id)
        self._playable=Event()
        self._song=None
        self._command=None
        playerthread=Thread(target=self._player, name="McFooDj")
        playerthread.setDaemon(1)
        playerthread.start()

    def _playfile(self, filename):
	SIZE = 4096

	file = McFoo.backend.file.audiofilechooser(filename)
	while 1:
	    (buff, bytes, bit) = file.read(SIZE)
	    if bytes == 0: break
	    self._audio_dev.play(buff, bytes)
	    while self._command != None:
		if self._command == "next":
		    self._command=None
		    return
		elif self._command == "pause":
		    while self._command == "pause":
			pass
		elif self._command == "play":
		    self._command=None
		    pass
		else:
		    raise "ugly"

    def set_next(self, song):
        # must not call unless .isdone() is true
        self._song=song
        self._playable.set()

    def isdone(self):
        return not self._playable.isSet()

    def next(self):
        self._command="next"

    def pause(self):
        self._command="pause"

    def play(self):
        self._command="play"
