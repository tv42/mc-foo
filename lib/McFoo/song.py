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

class Song(McFoo.playqueue.Playable, UserDict.UserDict):
    cur_songid = 0

    def __init__(self, backend, media, name, pri=100):
	self.priority=pri
        self.backend=backend
        self.media=makesafe(media)
        self.name=name
	self.filename='/var/lib/mc-foo/media/%s/%s/path/%s' % (self.backend, self.media, self.name)
	Song.cur_songid=Song.cur_songid+1
	self.id=Song.cur_songid
	self.data={} #TODO tags

    def __repr__(self):
	return '<song id:%s pri:%s filename:%s>' % (self.id, self.priority, self.filename)

    def __str__(self):
	s=str(self.id)+' '+self.filename+'\n'
	for tag in self.data.keys():
	    s=s+'  '+self.data[tag]+'\n'
	return s

    # this is for python 1.5, kill this when using 2.x
    def __cmp__(self, other):
        if isinstance(other, Song):
            return cmp(self.id, other.id)
	else:
            return 1

    def as_data(self):
        return {'id': self.id,
                'priority': self.priority,
                'backend': self.backend,
                'media': self.media,
                'name': self.name,
                }
