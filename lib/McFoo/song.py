import UserDict
import McFoo.playqueue

import string
safetable = string.maketrans('','')
allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
for i in range(256):
    if safetable[i] not in allowed:
        safetable=string.replace(safetable, safetable[i], '_')

def makesafe(s):
    return string.translate(s, safetable)

def get_comments(filename):
    import McFoo.backend.file
    try:
        return McFoo.backend.file.audiofilechooser(filename).comment()
    except (McFoo.backend.file.McFooBackendFileDoesNotExist,
            McFoo.backend.file.McFooBackendFileUnknownFormat):
        return {}

class Song(McFoo.playqueue.Playable, UserDict.UserDict):
    cur_songid = 1000

    def __init__(self, filename, pri=100):
        UserDict.UserDict.__init__(self)
	self.priority=pri
	self.filename=filename
	Song.cur_songid=Song.cur_songid+1
	self.id=Song.cur_songid
        self.data=get_comments(self.filename)

    def __getinitargs__(self):
        return [self.filename, self.priority]

    def __repr__(self):
	return '<song id:%s pri:%s filename:%s>' % (self.id, self.priority, self.filename)

    def __str__(self):
	s=str(self.id)+' '+self.filename+'\n'
	for tag in self.data.keys():
	    s=s+'  '+str(self.data[tag])+'\n'
	return s

    # this is for python 1.5, kill this when using 2.x
    def __cmp__(self, other):
        if isinstance(other, Song):
            return cmp(self.id, other.id)
	else:
            return 1

    def matchRegExp(self, regexp):
        if regexp.search(self.filename):
            return 1
        for k,vs in self.data.items():
            if regexp.search(k):
                return 1
            for v in vs:
                if regexp.search(v):
                    return 1
        return 0

    def as_data(self):
        return self.__getstate__()

    def __getstate__(self):
        return {'id': self.id,
                'priority': self.priority,
                'filename': self.filename,
                'data': self.data
                }
