class Ogg:
    def __init__(self, filename):
        import ogg.vorbis
        self.vf = ogg.vorbis.VorbisFile(filename)
    def read(self, size):
        return self.vf.read(size)

class Mp3:
    def __init__(self, filename):
	import popen2
	import string
 	self.fd_in, fd_out = popen2.popen2("mpg123 -s -@ -") #Eww
	fd_out.write("%s\n" % filename)
	fd_out.close()
    def read(self, size):
	foo = self.fd_in.read(size)
	return (foo, len(foo), 0)
    def __del__(self):
        self.fd_in.close()

def audiofilechooser(filename):
    import string
    ext = string.lower(filename)[-4:]
    if ext == '.ogg':
	return Ogg(filename)
    elif ext == '.mp3':
	return Mp3(filename)
    else:
	return None
