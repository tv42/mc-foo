import asynchat

class asyncreadline(asynchat.async_chat):
    def __init__(self, socket):
	asynchat.async_chat.__init__(self, socket)
	self.set_terminator('\n')
	self.line = ''

    def collect_incoming_data(self, data):
	self.line = self.line + data

    def found_terminator(self):
        try:
            self.process(self.line)
        except:
            self.line = ''
            raise
        self.line = ''

    def process(self, line):
        pass
