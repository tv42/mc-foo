class Queueable:
    def playable(self):
	raise "Queueable base class method playable called"

class Playable(Queueable):
    id=None

    def playable(self):
	return 1

class NonPlayable(Queueable):
    def playable(self):
	return 0

class McFooPriorityMarker(NonPlayable):
    def __init__(self, pri):
	self.priority=pri

    def __repr__(self):
	return '<priority %d>' % self.priority

    def as_data(self):
        return {'priority': self.priority}

import UserList
class PlayHistory(UserList.UserList):
    def __init__(self):
        UserList.UserList.__init__(self)
        self.maxlen=10

    def add(self, song):
        if song!=None:
            self[0:0]=[song]
        self[self.maxlen:]=[]

    def as_data(self):
        s=map(lambda s: s.as_data(), self.data)
        s.reverse()
        return s

#TODO protect threads from eachother
class PlayQueue(UserList.UserList):
    def __init__(self):
        UserList.UserList.__init__(self)
        self.data=[]
        self.history=PlayHistory()

    def insert_point(self, pri):
	smallest=0
	for i in range(len(self.data)):
	    if isinstance(self[i], McFooPriorityMarker):
		if pri == self[i].priority:
		    return i
		elif pri < self[i].priority:
		    break
		else:
		    smallest=i
	self.insert(smallest, McFooPriorityMarker(pri))
	return smallest

    def add(self, song):
	self.data.insert(self.insert_point(song.priority), song)

    def remove(self, song):
        i=0
        while song!=self[i]:
            i=i+1
        self[i:i]=[]

    def remove_by_id(self, id):
        i=0
        while not self[i].playable() or id!=self[i].id:
            i=i+1
        self[i:i+1]=[]

    def pop(self):
	i=0
	try:
            while not self[i].playable():
		i=i+1
	    song=self[i]
	    del self[i]
	except IndexError:
	    song=None
        self.history.add(song)
	return song

    def __str__(self):
	s=''
	for so in self.data:
	    s=s+str(so)
	return s

    def as_data(self):
        s=[]
        for song in self:
            s.append(song.as_data())
        return {'history': self.history.as_data(), 'queue': s}

    def move(self, id, offset):
        i=0
        while not self[i].playable() or id!=self[i].id:
            i=i+1
        t=self[i]
        self[i:i+1]=[]
        self.insert(i+offset, t)
