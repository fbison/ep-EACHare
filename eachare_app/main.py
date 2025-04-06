import sys
from eachare_app.connection import Connection
from eachare_app.peer_manager import PeerManager
from eachare_app.peer import Peer
import os
# Exit constant
EXIT_COMMAND = 9

peer_manager = PeerManager()
_shared_dir= ""

def hello(peer: Peer):
    connection.send_message(peer, "HELLO")

def get_peers():
    peers = peer_manager.list_peers()
    for peer in peers:
        connection.send_message(peer, "GET_PEERS")

def list_local_files():
    if not _shared_dir:
        print("Erro: O diretório compartilhado não foi configurado.")
        return

    try:
        files = os.listdir(_shared_dir)
        if files:
            for file in files:
                print(f"\t{file}")
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")

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
    for peer in peer_manager.get_online_peers():
        connection.send_message(peer, "BYE")
    connection.stop()
    sys.exit()

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
        print("Lista de peers:")
        print("\t[0] voltar para o menu anterior")
        for index, peer in enumerate(peers, start=1):
            print(f"\t[{index}] {peer.ip}:{peer.port} {'ONLINE' if peer.online else 'OFFLINE'}")
        command_number = int(input(">"))
        if command_number == 0:
            break
        if command_number > len(peers):
            print("Por favor, insira um número válido.")
            continue
        function(peers[command_number-1])

def list_peers():
    peers= peer_manager.list_peers()
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

def verify_shared_dir(shared_dir: str) -> None:
    shared_dir = os.path.abspath(shared_dir)  # Resolve to absolute path
    if not os.path.exists(shared_dir):
        raise RuntimeError(f"Erro: O diretório compartilhado '{shared_dir}' não existe.")
    if not os.path.isdir(shared_dir):
        raise RuntimeError(f"Erro: O caminho '{shared_dir}' não é um diretório.")
    if not os.access(shared_dir, os.R_OK):
        raise RuntimeError(f"Erro: O diretório compartilhado '{shared_dir}' não é acessível para leitura.")
    global _shared_dir 
    _shared_dir = shared_dir

def main():
    if len(sys.argv) != 4:
        print("Uso: ./eachare <endereço:porta> <vizinhos.txt> <diretorio_compartilhado>")
        sys.exit(1)

    address, port = sys.argv[1].split(':')
    peers_file = sys.argv[2]
    verify_shared_dir(sys.argv[3])

    global connection #TODO: Verificar se é uma boa prática e o melhor jeito de fazer isso
    connection = Connection(address, port, peer_manager)
    
    #TODO criar conexão TCP com adress e port
    try:
        read_peers(peers_file, peer_manager)
        #TODO Verificar se o diretório de compartilhamento é válido 
        connection.start_server() # Após ler os peers, inicia o servidor, conforme a especificação
        menu()
    except RuntimeError as error:
        print(error)

if __name__ == '__main__':
    main()
