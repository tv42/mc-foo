import UserList
import twisted.spread.pb

class Observers(UserList.UserList):
    def __init__(self, data=[]):
        UserList.UserList.__init__(self, data)

    def __call__(self, func, *a, **kw):
        for obs in self:
            apply(getattr(obs, func), a, kw)
                
    def append_and_call(self, obs, func, *a, **kw):
        apply(getattr(obs, func), a, kw)
        self.append(obs)

class Observer(twisted.spread.pb.Referenceable):
    def __init__(self):
        pass
