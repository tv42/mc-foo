import ID3
import string
import exceptions
import os.path

from errno import ENOENT

McFooBackendFileUnknownFormat='McFooBackendFileUnknownFormat'
McFooBackendFileDoesNotExist='McFooBackendFileDoesNotExist'

class Ogg:
    def __init__(self, filename):
        import ogg.vorbis
        try:
            self.vf = ogg.vorbis.VorbisFile(filename)
        except IOError, e:
            # ogg.vorbis.VorbisFile fails to set errno properly! TODO fix it.
            if e.errno == ENOENT \
               or (e.errno==None and e.args[0].startswith("Could not open file:")):
                raise McFooBackendFileDoesNotExist
            else:
                print repr(e), dir(e)
                print e.args
                print e.errno
                raise
    def start_play(self):
        pass
    def read(self, size):
        return self.vf.read(size)
    def comment(self):
        r={}
        try:
            r=self.vf.comment().as_dict()
        except exceptions.UnicodeError:
            pass
        for key in r.keys():
            # twisted can't make unicode's persistent
            r[key]=map(lambda s: s.encode('latin-1'), r[key])
        return r
    def time_total(self):
        return self.vf.time_total(0)
    def time_tell(self):
        return self.vf.time_tell()
    def time_seek(self, secs):
        return self.vf.time_seek(secs)

class Mp3:
    def __init__(self, filename):
        self.filename=filename
        self.fd_in=None
        if not os.path.isfile(filename):
            raise McFooBackendFileDoesNotExist
    def start_play(self):
	import popen2
 	self.fd_in, fd_out = popen2.popen2("mpg321 -s -@ -") #Eww
        # TODO mpg321 -R - -w /dev/fd/2
	fd_out.write("%s\n" % self.filename)
	fd_out.close()
    def read(self, size):
	foo = self.fd_in.read(size)
	return (foo, len(foo), 0)
    def __del__(self):
        if self.fd_in!=None:
            self.fd_in.close()
    def comment(self):
        try:
            id3=ID3.ID3(self.filename)
        except ID3.InvalidTagError:
            return {}

        c={}
        c['TITLE']=[string.strip(id3.title)]
        c['ARTIST']=[string.strip(id3.artist)]
        c['ALBUM']=[string.strip(id3.album)]
        c['YEAR']=[string.strip(id3.year)]
        genre=id3.genre
        try:
            genre=id3.genres[genre]
        except IndexError:
            genre=str(genre)
        c['GENRE']=genre
        c['COMMENT']=[string.strip(id3.comment)]
        for key in c.keys():
            if len(c[key])==1 and c[key][0]=='':
                del c[key]
        return c
    def time_total(self):
        return 0
    def time_tell(self):
        return 0
    def time_seek(self, secs):
        pass

def audiofilechooser(filename):
    import string
    ext = string.lower(filename)[-4:]
    if ext == '.ogg':
        return Ogg(filename)
    elif ext == '.mp3':
	return Mp3(filename)
    else:
        raise McFooBackendFileUnknownFormat, \
              ("Unknown file format:", filename)

