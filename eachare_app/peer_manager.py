from eachare_app.peer import Peer
from threading import Lock

class PeerManager:
    def __init__(self):
        self.peers: dict[tuple[str, int], Peer] = {}
        self.lock = Lock()

    #TODO Verificar se imprimimos logs nossos ou só deixamos comentado para ficar só os do professor impressos

    def add_peer(self, ip: str, port: int) -> None:
        with self.lock:
            if (ip, port) in self.peers:
                return
            self.peers[(ip, port)] = Peer(ip, port)
        print(f"Adicionando novo peer {ip}:{port} status OFFLINE")
    
    def add_peer_with_details(self, ip: str, port: int, online: bool, mysterious_number: int) -> None:
        with self.lock:
            peer = self.peers.get((ip, port))
            if not peer:
                self.peers[(ip, port)] = Peer(ip, port, online=online, mysterious_number=mysterious_number)
                return
        # Perform operations on the peer outside the lock
        peer.set_online() if online else peer.set_offline()
        peer.set_mysterious_number(mysterious_number)

    def add_online_peer(self, ip: str, port: int) -> None:
        with self.lock:
            peer = self.peers.get((ip, port))
            if not peer:
                self.peers[(ip, port)] = Peer(ip, port, True)
                print(f"\tAdicionando novo peer {ip}:{port} status ONLINE")
                return
        peer.set_online()

    def get_peer(self, ip: str, port: int) -> Peer:
        with self.lock:
            return self.peers[(ip, port)]

    def list_peers(self) -> list[Peer]:
        with self.lock:
            return list(self.peers.values())
    
    def list_peers_message(self, sender_peer: Peer) -> str:
        with self.lock:
            peers = list(self.peers.values())
        # Perform filtering and formatting outside the lock
        return " ".join(peer.describe_as_message() for peer in peers if peer != sender_peer)

    def get_online_peers(self) -> list[Peer]:
        with self.lock:
            peers = list(self.peers.values())  # Safely retrieve peer values
        # Perform filtering outside the lock
        return [peer for peer in peers if peer.online]
    
    def number_of_peers(self) -> int:
        with self.lock:
            return len(self.peers)
