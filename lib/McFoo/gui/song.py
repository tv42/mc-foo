import UserDict

class GuiSong(UserDict.UserDict):
    def __init__(self, data={}):
        UserDict.UserDict.__init__(self, data)

    def __str__(self):
        if self.data.has_key('comment') \
           and self.data['comment'].has_key('ARTIST') \
           and self.data['comment'].has_key('TITLE') \
           and filter(lambda x: x!="", self.data['comment']['ARTIST'])!=[] \
           and filter(lambda x: x!="", self.data['comment']['TITLE'])!=[]:
            return str(filter(lambda x: x!="", self.data['comment']['ARTIST'])[0]) \
                   +': '+str(filter(lambda x: x!="", self.data['comment']['TITLE'])[0])
        elif self.data.has_key('name'):
            return self.data['name']
        else:
            return repr(self)
