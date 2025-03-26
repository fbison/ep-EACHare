class Peer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.online = False

    def set_online(self):
        self.online = True
    
    def set_offline(self):
        self.online = False