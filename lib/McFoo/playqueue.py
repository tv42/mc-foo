import twisted.spread.pb
import McFoo.observe

class HistoryObserver(McFoo.observe.Observer):
    def remote_snapshot(self, history):
        pass

    def remote_add(self, entry):
        pass

class PlayqueueObserver(McFoo.observe.Observer):
    def remote_snapshot(self, queue):
        pass

    def remote_insert(self, idx, song):
        pass

    def remote_remove(self, idx):
        pass

    def remote_move(self, oldidx, newidx):
        pass


class Queueable:
    def playable(self):
        raise NotImplementedError

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
    def __init__(self, initlist=[]):
        UserList.UserList.__init__(self, initlist)
        self.maxlen=10
        self.observers=McFoo.observe.Observers()

    def __getinitargs__(self):
        return [self.data]

    def add(self, song):
        if song!=None:
            self[0:0]=[song]
        self[self.maxlen:]=[]
        self.observers('add', song.as_data())

    def as_data(self):
        s=map(lambda s: s.as_data(), self.data)
        s.reverse()
        return s

    def observe(self, callback):
        self.observers.append_and_call(callback, 'snapshot', self.as_data())

    def unobserve(self, callback):
        self.observers.remove(callback)

class PlayQueue(UserList.UserList):
    def __init__(self, filler, initlist=[]):
        UserList.UserList.__init__(self, initlist)
        self.history=PlayHistory()
        self.observers=McFoo.observe.Observers()
        self.filler=filler

    def __getinitargs__(self):
        return [self.filler, self.data]

    def observe(self, callback):
        self.observers.append_and_call(callback, 'snapshot', self.as_data())

    def unobserve(self, callback):
        self.observers.remove(callback)

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
	self.insert(self.insert_point(song.priority), song)

    def _insert(self, idx, song):
        self.data.insert(idx, song)

    def insert(self, idx, song):
	self._insert(idx, song)
        self.observers('insert', idx, song.as_data())

    def remove(self, song):
        i=0
        while song!=self[i]:
            i=i+1
        self[i:i+1]=[]
        self.observers('remove', i)
        self.ensure_fill()

    def id2idx(self, id):
        i=0
        while not self[i].playable() or id!=self[i].id:
            i=i+1
        return i

    def remove_by_id(self, id):
        try:
            i=self.id2idx(id)
        except IndexError:
            pass
        else:
            self[i:i+1]=[]
            self.observers('remove', i)
            self.ensure_fill()

    def pop(self):
        self.ensure_fill()
	i=0
	try:
            while not self[i].playable():
		i=i+1
	    song=self[i]
	    del self[i]
	except IndexError:
	    song=None

        if song:
            self.observers('remove', i)
            self.history.add(song)

	return song

    def ensure_fill(self):
        while len(self) < 100:
            filename=self.filler()
            song=McFoo.song.Song(filename)
            self.add(song)

    def __str__(self):
	s=''
	for so in self.data:
	    s=s+str(so)
	return s

    def as_data(self):
        s=[]
        for song in self:
            s.append(song.as_data())
        return s

    def move(self, id, offset):
        try:
            i=self.id2idx(id)
        except IndexError:
            pass
        else:
            t=self[i]
            self[i:i+1]=[]
            self._insert(i+offset, t)
            self.observers('move', i, i+offset)

    def moveabs(self, id, newloc):
        try:
            i=self.id2idx(id)
        except IndexError:
            pass
        else:
            t=self[i]
            self[i:i+1]=[]
            self._insert(newloc, t)
            self.observers('move', i, newloc)
