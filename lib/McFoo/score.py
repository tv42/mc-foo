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

    def getScore(self, filename):
        #TODO
        return 0

    def as_data(self):
        return self.data

class SongProfile(UserDict.UserDict):
    def incScore(self, filename, inc=1):
        if not self.data.has_key(filename):
            self.data[filename]=0

        self.data[filename]+=inc

        if self.data[filename]==0:
            del self.data[filename]

    def as_data(self):
        return self.data

    def getScore(self, filename):
        return self.get(filename, 0)

class Profile:
    def __init__(self):
        self.songs=SongProfile()
        self.tags=TagProfile()
        self.include=[]

    def as_data(self):
        return {'include': self.include,
                'songs': self.songs.as_data(),
                'tags': self.tags.as_data()}

    def getScore(self, filename):
        return self.songs.getScore(filename) + self.tags.getScore(filename)

    def incScore(self, filename, inc=1):
        self.songs.incScore(filename, inc)

    def __repr__(self):
        return repr(self.as_data())

class UserProfile(UserDict.UserDict):
    def __init__(self):
        UserDict.UserDict.__init__(self)
        self.data['default']=Profile()
        self.def_read=['default']
        self.def_write=['default']

    def incScore(self, filename, inc=1):
        profileName=self.def_write[0]
        del self.def_write[0]
        self.def_write.append(profileName)

        print "profile %s=%s"%(profileName, repr(self[profileName]))
        self[profileName].incScore(filename, inc)

    def addprofile(self, profilename):
        if not self.data.has_key(profilename):
            self.data[profilename]=Profile()
        return self.data[profilename]

    def getScore(self, filename):
        sum=0
        for profileName in self.def_read:
            sum+=self[profileName].getScore(filename)
        return sum

class ProfileTable(UserDict.UserDict):
    def __init__(self):
        UserDict.UserDict.__init__(self)

    def adduser(self, user):
        if not self.data.has_key(user):
            self.data[user]=UserProfile()
        return self.data[user]

    def getScore(self, filename):
        sum=0
        for user, profile in self.items():
            sum+=profile.getScore(filename)
        return sum
