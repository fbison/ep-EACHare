import sys
from socket import socket
from collections import OrderedDict
from connection import Connection
from peerManager import PeerManager
from peer import Peer
# Exit constant
EXIT_COMMAND = 9

peerManager = PeerManager()

def get_peers():
    print("")
    #TODO: Implementation

def list_local_files():
    print("")
    #TODO: Implementation

def search_files():
    print("")
    #TODO: Implementation

def show_statistics():
    print("")
    #TODO: Implementation

def change_chunk_size():
    print("")
    #TODO: Implementation

def exit():
    print("")
    #TODO: Implementation e envio das mensagens BYE para que os outros peers alterem o estado do peer como offline


def show_commands():
    print("Escolha um comando:")
    for key, value in commands_functions.items():
        print(f"\t[{key}] {value['description']}")

def execute_command(command_number):
    if command_number not in commands_functions:
        raise ValueError()
    commands_functions[command_number]["function"]()

def menu():
    while True:
        show_commands()
        try:
            command_number = int(input(">"))
            if command_number == int(EXIT_COMMAND):
                commands_functions[command_number]["function"]()
                break
            execute_command(command_number)
        except ValueError:
            print("Por favor, insira um número válido.")

def read_peers(peers_file: str, peer_manager: PeerManager) -> None:
    try:
        with open(peers_file, 'r') as file:
            for line in file:
                address, port = line.strip().split(':')
                peer_manager.add_peer(address, int(port))
    except FileNotFoundError:
        raise RuntimeError(f"Erro: O arquivo {peers_file} não foi encontrado.")
    except ValueError:
        raise RuntimeError("Erro: O arquivo de peers contém uma linha inválida.")

#TODO: Verificar se o menu de peers deve ficar iterando até a pessoa sair 
# ou após mandar um HELLO ele retorna para o menu anterior

def menu_peers(peers: list[Peer], function: callable) -> None:
    while True:
        print("\t [0] voltar para o menu anterior")
        for index, peer in enumerate(peers, start=1):
            print(f"\t [{index}] {peer.ip}:{peer.port} {'ONLINE' if peer.online else 'OFFLINE'}")
        command_number = int(input(">"))
        if command_number == 0:
            break
        if command_number > len(peers):
            print("Por favor, insira um número válido.")
            continue
        function(peers[command_number-1])

def hello(peer: Peer):
    connection.send_message(peer, "HELLO")

def list_peers():
    peers= peerManager.list_peers()
    menu_peers(peers, hello)
    
commands_functions = {
    1: {"description": "Listar peers", "function": list_peers},
    2: {"description": "Obter peers", "function": get_peers},
    3: {"description": "Listar arquivos locais", "function": list_local_files},
    4: {"description": "Buscar arquivos", "function": search_files},
    5: {"description": "Exibir estatisticas", "function": show_statistics},
    6: {"description": "Alterar tamanho de chunk", "function": change_chunk_size},
    EXIT_COMMAND: {"description": "Sair", "function": exit}
}
def main():
    address, port = sys.argv[1].split(':')
    peers_file = sys.argv[2]
    shared_dir = sys.argv[3]

    global connection #TODO: Verificar se é uma boa prática e o melhor jeito de fazer isso
    connection = Connection(address, port)
    connection.start_server()
    #Eu não coloquei o start_server no innit do connection, mas pode ser uma possibilidade,
    #seria mais acoplado, mas não sei se haverá uma situação em que a classe será iniciada sem precisar da conexão
    
    #TODO criar conexão TCP com adress e port
    try:
        read_peers(peers_file, peerManager)
        #TODO Verificar se o diretório de compartilhamento é válido 
        menu()
    except RuntimeError as error:
        print(error)

if __name__ == '__main__':
    main()
