import UserList
import twisted.spread.pb

class ObserverLostConnection:
    def __init__(self, observers, guilty):
        self.obs=observers
        self.guilty=guilty

    def __call__(self, tb):
        if tb==twisted.spread.pb.PB_CONNECTION_LOST:
            self.obs.remove(self.guilty)
        else:
            twisted.spread.pb.printTraceback(tb)

class Observers(UserList.UserList):
    def __init__(self, data=[]):
        UserList.UserList.__init__(self, data)

    def __call__(self, func, *a, **kw):
        for obs in self:
            if not kw.has_key('pberrback'):
                kw['pberrback']=ObserverLostConnection(self, obs)
            apply(getattr(obs, func), a, kw)
                
    def append_and_call(self, obs, func, *a, **kw):
        try:
            apply(getattr(obs, func), a, kw)
        except ObserverLostException:
            pass
        else:
            self.append(obs)
