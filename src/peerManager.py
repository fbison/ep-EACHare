from peer import Peer

class PeerManager:
    def __init__(self):
        self.peers: dict[tuple[str, int], Peer] = {}

    def add_peer(self, ip: str, port: int) -> None:
        self.peers[(ip, port)] = Peer(ip, port)
        print(f"Adicionando novo peer {ip}:{port} status OFFLINE")

    def get_peer(self, ip: str, port: int) -> Peer:
        return self.peers[(ip, port)]

    #TODO: Verificar se vale a pena essa função ser responsável pela impressão do menu, 
    #ou deixamos ela só retornar a lista de peers e outra função cuidar da lógica desse menu
    def list_peers(self) -> list[Peer]:
        return list(self.peers.values())

    def get_online_peers(self) -> list[Peer]:
        return [peer for peer in self.peers.values() if peer.online]
