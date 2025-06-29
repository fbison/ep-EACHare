import threading
from eachare_app.utils import print_with_lock

class Peer:
    def __init__(self, ip, port, online=False, clock=0):
        self.ip = ip
        self.port = port
        self.online = online
        self.clock = clock
        self.lock = threading.Lock()
    
    def describe_as_message(self):
        with self.lock:
            status = "ONLINE" if self.online else "OFFLINE"
            return f"{self.ip}:{self.port}:{status}:{self.clock}"

    def set_clock(self, clock: int):
        with self.lock:
            self.clock = clock

    def set_online(self):
        with self.lock:
            self.online = True
            print_with_lock(f"\tAtualizando peer {self.ip}:{self.port} status ONLINE")
    
    def set_offline(self):
        with self.lock:
            self.online = False
            print_with_lock(f"\tAtualizando peer {self.ip}:{self.port} status OFFLINE")
