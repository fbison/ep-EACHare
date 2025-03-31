class Peer:
    def __init__(self, ip, port, online=False, mysterious_number=0):
        self.ip = ip
        self.port = port
        self.online = online
        self.mysterious_number=mysterious_number

    def describe_as_message(self):
        status = "ONLINE" if self.online else "OFFLINE"
        return f"{self.ip}:{self.port}:{status}:{self.mysterious_number}"

    
    def set_mysterious_number(self, number:int):
        self.mysterious_number = number

    def set_online(self):
        self.online = True
        print(f"Atualizando peer {self.ip}:{self.port} status ONLINE")
    
    def set_offline(self):
        self.online = False
        print(f"Atualizando peer {self.ip}:{self.port} status OFFLINE")
