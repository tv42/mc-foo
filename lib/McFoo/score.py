import UserDict

class TagProfile(UserDict.UserDict):
    def opinion_on_tag(self, tagname, tagvalue, adjust):
        if not self.data.has_key(tagname):
            self.data[tagname]={}
        if not self.data[tagname].has_key(tagvalue):
            self.data[tagname][tagvalue]=0

        self.data[tagname][tagvalue]=self.data[tagname][tagvalue]+adjust

        if self.data[tagname][tagvalue]==0:
            del self.data[tagname][tagvalue]
        if self.data[tagname]=={}:
            del self.data[tagname]

    def as_data(self):
        return self.data

class SongProfile(UserDict.UserDict):
    def opinion_on_song(self, song, adjust):
        if not self.data.has_key(song.backend):
            self.data[song.backend]={}
        if not self.data[song.backend].has_key(song.media):
            self.data[song.backend][song.media]={}
        if not self.data[song.backend][song.media].has_key(song.name):
            self.data[song.backend][song.media][song.name]=0

        self.data[song.backend][song.media][song.name]=self.data[song.backend][song.media][song.name]+adjust

        if self.data[song.backend][song.media][song.name]==0:
            del self.data[song.backend][song.media][song.name]
        if self.data[song.backend][song.media]=={}:
            del self.data[song.backend][song.media]
        if self.data[song.backend]=={}:
            del self.data[song.backend]

    def as_data(self):
        return self.data


class Profile:
    def __init__(self):
        self.songs=SongProfile()
        self.tags=TagProfile()
        self.include=[]

    def as_data(self):
        return {'include': self.include,
                'songs': self.songs.as_data(),
                'tags': self.tags.as_data()}

    def __repr__(self):
        return repr(self.as_data())

class UserProfile(UserDict.UserDict):
    def __init__(self):
        UserDict.UserDict.__init__(self)
        self.data['default']={}
        self.def_read=[]
        self.def_write=[]

    def addprofile(self, profilename):
        if not self.data.has_key(profilename):
            self.data[profilename]=Profile()
        return self.data[profilename]

class ProfileTable(UserDict.UserDict):
    def __init__(self):
        UserDict.UserDict.__init__(self)

    def adduser(self, user):
        if not self.data.has_key(user):
            self.data[user]=UserProfile()
        return self.data[user]
