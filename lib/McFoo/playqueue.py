class Queueable:
    def playable(self):
	raise "Queueable base class method playable called"

class Playable(Queueable):
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

import UserList
#TODO protect threads from eachother
class PlayQueue(UserList.UserList):
    def __init__(self):
        self.data=[]

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
	self.data[song.priority].remove(song)

    def pop(self):
	i=0
	try:
	    while not self[i].playable():
		i=i+1
	    song=self[i]
	    del self[i]
	except IndexError:
	    song=None
	return song

    def __str__(self):
	s=''
	for so in self.data:
	    s=s+str(so)
	return s
