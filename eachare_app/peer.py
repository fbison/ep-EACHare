import threading

class Peer:
    def __init__(self, ip, port, online=False, mysterious_number=0):
        self.ip = ip
        self.port = port
        self.online = online
        self.mysterious_number = mysterious_number
        self.lock = threading.Lock()
    
    def describe_as_message(self):
        with self.lock:
            status = "ONLINE" if self.online else "OFFLINE"
            return f"{self.ip}:{self.port}:{status}:{self.mysterious_number}"

    def set_mysterious_number(self, number: int):
        with self.lock:
            self.mysterious_number = number

    def set_online(self):
        with self.lock:
            self.online = True
            print(f"\tAtualizando peer {self.ip}:{self.port} status ONLINE")
    
    def set_offline(self):
        with self.lock:
            self.online = False
            print(f"\tAtualizando peer {self.ip}:{self.port} status OFFLINE")
