class Peer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.online = False

    def set_online(self):
        self.online = True
        print(f"Atualizando peer {self.ip}:{self.port} status ONLINE")
    
    def set_offline(self):
        self.online = False
        print(f"Atualizando peer {self.ip}:{self.port} status OFFLINE")
