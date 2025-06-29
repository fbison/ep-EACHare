from eachare_app.peer_manager import PeerManager
from eachare_app.connection import Connection
from eachare_app.utils import print_with_lock

# Instancia o PeerManager e Connection
pm = PeerManager()
conn = Connection('127.0.0.1', 8080, pm)

# Simula recebimento de uma lista de peers
# Formato: <ip:porta> <clock> PEER_LIST <peer1> <peer2> ...
peer_list_message = "127.0.0.1:8081 2 PEER_LIST 2 127.0.0.1:8083:ONLINE:5 127.0.0.1:8082:OFFLINE:3"
conn.handle_message(peer_list_message, None)

def print_peer_list():
    peers = pm.list_peers()
    print_with_lock("Lista de peers:")
    for peer in peers:
        print_with_lock(f"{peer.ip}:{peer.port} online={peer.online} clock={peer.clock}")

print_peer_list()

# Simula recebimento de outra lista de peers
peer_list_message = "127.0.0.1:8081 1 PEER_LIST 2 127.0.0.1:8083:ONLINE:3 127.0.0.1:8082:OFFLINE:4"
conn.handle_message(peer_list_message, None)
print_with_lock("\nApós receber nova lista de peers:")

print_peer_list()
