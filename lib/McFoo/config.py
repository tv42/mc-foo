import os

class ConfigStore:
    host=None
    port=None

    def __init__(self):
        if self.host==None:
            try:
                self.host=os.environ['MCFOOHOST']
            except KeyError:
                self.host='localhost'

        if self.port==None:
            try:
                self.port=int(os.environ['MCFOOPORT'])
            except KeyError:
                self.port=25706

store = ConfigStore()
