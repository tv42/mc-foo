import UserDict
import McFoo.playqueue
class Song(McFoo.playqueue.Playable, UserDict.UserDict):
    cur_songid = 0

    def __init__(self, filename, pri=100):
	self.priority=pri
	self.filename=filename
	Song.cur_songid=Song.cur_songid+1
	self.id=Song.cur_songid
	self.data={} #TODO tags

#    def random(self):
#        import random
#        import linecache
#        s=random.choice(linecache.getlines("/data/music/oggs"))
#        return s[:-1]

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
