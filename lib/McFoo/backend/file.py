import ID3Tag
import string

class Ogg:
    def __init__(self, filename):
        import ogg.vorbis
        self.vf = ogg.vorbis.VorbisFile(filename)
    def start_play(self):
        pass
    def read(self, size):
        return self.vf.read(size)
    def comment(self):
        return self.vf.comment().as_dict()

class Mp3:
    def __init__(self, filename):
        self.filename=filename
        self.fd_in=None
    def start_play(self):
	import popen2
 	self.fd_in, fd_out = popen2.popen2("mpg123 -s -@ -") #Eww
	fd_out.write("%s\n" % self.filename)
	fd_out.close()
    def read(self, size):
	foo = self.fd_in.read(size)
	return (foo, len(foo), 0)
    def __del__(self):
        if self.fd_in!=None:
            self.fd_in.close()
    def comment(self):
        c={}
        id3=ID3Tag.ID3Tag(self.filename)
        try:
            id3.Read()
            c={'TITLE': [string.strip(id3.theTitle())],
               'ARTIST': [string.strip(id3.theArtist())],
               'ALBUM': [string.strip(id3.theAlbum())],
               'YEAR': [string.strip(id3.theYear())],
               'GENRE': [id3.theGenre()],
               'COMMENT': [string.strip(id3.theComment())]}
        except StandardError, exception:
            s="No TAG header found in MP3 file:"
            strerror=exception.args[0]
            if string.find(strerror, s, 0, len(s))==0:
                pass
            else:
                raise
        for key in c.keys():
            if c[key]=='':
                c.delete[key]
        return c

def audiofilechooser(filename):
    import string
    ext = string.lower(filename)[-4:]
    if ext == '.ogg':
	return Ogg(filename)
    elif ext == '.mp3':
	return Mp3(filename)
    else:
	return None
