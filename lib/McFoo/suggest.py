import os, os.path, random

class Cyclic:

    """A cyclic sequence of things. Ask stuff from me with get()
    and it won't repeat often."""
    
    chunksize=1000

    def __init__(self, initlist):
        assert initlist
        if len(initlist)/2 < self.chunksize:
            self.chunksize=len(initlist)/2
        random.shuffle(initlist)
        self.next=initlist[:self.chunksize]
        self.rest=initlist[self.chunksize:]
        self._feed_next()

    def _random_insert_rest(self, weight, item):
        max=len(self.rest)+1
        max=int(max / 2**(weight/10.0))
        if max==0:
            max=1
        i=random.randrange(max)
        self.rest[i:i]=[(weight, item)]

    def _feed_next(self):
        need=self.chunksize-len(self.next)
        if need>0:
            self.next.extend(self.rest[:need])
            del self.rest[:need]
            assert len(self.next) == self.chunksize

    def get(self):
        weight, item=self.next[0]
        self._random_insert_rest(weight, item)
        del self.next[0]
        self._feed_next()
        return item

    def peek(self):
        """Provide a read-only view to first chunksize items."""
        return self.next


class Suggestions:
    def __init__(self, paths, profileTable):
        self.paths=paths
        self.data=None
        self.profileTable=profileTable

    def __getinitargs__(self):
        return [self.paths, self.profileTable]

    def _visit(self, songs, dirname, names):
        for file in os.listdir(dirname):
            l=file.lower()
            if l.endswith(".mp3") or l.endswith(".ogg"):
                filename=dirname+'/'+file
                score=self.profileTable.getScore(filename)
                songs.append((score, filename))

    def get(self):
        if not self.data:
            songs=[]
            for path in self.paths:
                os.path.walk(path, self._visit, songs)
            self.data=Cyclic(songs)
        return self.data.get()
