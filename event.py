class Event:
    def __init__(self,time, type, client=None):
        self.time = time
        self.type = type
        self.client = client
    
    def __lt__(self, other):
        return self.time < other.time