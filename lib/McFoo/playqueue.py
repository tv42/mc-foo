import twisted.spread.pb

class HistoryObserver(twisted.spread.pb.Referenced):
    def __init__(self):
        pass

    def remote_snapshot(self, history):
        pass

    def remote_add(self, entry):
        pass

class PlayqueueObserver(twisted.spread.pb.Referenced):
    def __init__(self):
        pass

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
        self.observers=[]

    def add(self, song):
        if song!=None:
            self[0:0]=[song]
        self[self.maxlen:]=[]
        for callback in self.observers:
            callback.add(song.as_data())

    def as_data(self):
        s=map(lambda s: s.as_data(), self.data)
        s.reverse()
        return s

    def observe(self, callback):
        callback.snapshot(self.as_data())
        self.observers.append(callback)

#TODO protect threads from eachother
class PlayQueue(UserList.UserList):
    filler=None

    def __init__(self):
        UserList.UserList.__init__(self)
        self.data=[]
        self.history=PlayHistory()
        self.observers=[]

    def observe(self, callback):
        callback.snapshot(self.as_data())
        self.observers.append(callback)

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
        for callback in self.observers:
            callback.insert(idx, song.as_data())

    def remove(self, song):
        i=0
        while song!=self[i]:
            i=i+1
        self[i:i+1]=[]
        for callback in self.observers:
            callback.remove(i)
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
            for callback in self.observers:
                callback.remove(i)
            self.ensure_fill()

    def pop(self):
	i=0
	try:
            while not self[i].playable():
		i=i+1
	    song=self[i]
	    del self[i]
	except IndexError:
	    song=None

        if song:
            for callback in self.observers:
                callback.remove(i)
            self.history.add(song)

        self.ensure_fill()
	return song

    def ensure_fill(self):
        if len(self) < 100 and self.filler:
                self.filler()

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
            for callback in self.observers:
                callback.move(i, i+offset)

    def moveabs(self, id, newloc):
        try:
            i=self.id2idx(id)
        except IndexError:
            pass
        else:
            t=self[i]
            self[i:i+1]=[]
            self._insert(newloc, t)
            for callback in self.observers:
                callback.move(i, newloc)
