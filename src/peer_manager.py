from peer import Peer

class PeerManager:
    def __init__(self):
        self.peers: dict[tuple[str, int], Peer] = {}

    #TODO Verificar se imprimimos logs nossos ou só deixamos comentado para ficar só os do professor impressos

    def is_peer(self, ip: str, port: int) -> bool:
        return (ip, port) in self.peers

    def add_peer(self, ip: str, port: int) -> None:
        if self.is_peer(ip, port):
            return
        self.peers[(ip, port)] = Peer(ip, port)
    
    def add_peer_with_details(self, ip: str, port: int, online: bool, mysterious_number: int) -> None:
        if self.is_peer(ip, port):
            self.get_peer(ip, port).set_online() if online else self.get_peer(ip, port).set_offline()
            self.get_peer(ip, port).set_mysterious_number(mysterious_number)
            return
        self.peers[(ip, port)] = Peer(ip, port, online=online, mysterious_number=mysterious_number)

    def add_online_peer(self, ip: str, port: int) -> None:
        if self.is_peer(ip, port):
            peer = self.get_peer(ip, port)
            peer.set_online()
        self.peers[(ip, port)] = Peer(ip, port, True)

    def get_peer(self, ip: str, port: int) -> Peer:
        return self.peers[(ip, port)]

    def list_peers(self) -> list[Peer]:
        return list(self.peers.values())
    
    def list_peers_message(self) -> str:
        return "\n".join(peer.describe_as_message() for peer in self.list_peers() if peer.describe_as_message())

    def get_online_peers(self) -> list[Peer]:
        return [peer for peer in self.peers.values() if peer.online]
    
    def number_of_peers(self) -> int:
        return len(self.peers)
