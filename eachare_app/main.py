import sys
from eachare_app.connection import Connection
from eachare_app.peer_manager import PeerManager
from eachare_app.peer import Peer
import os
import threading
import base64
from eachare_app.config import set_shared_dir, get_shared_dir
# Exit constant
EXIT_COMMAND = 9

peer_manager = PeerManager()

def hello(peer: Peer):
    connection.send_message(peer, "HELLO")

def get_peers():
    peers = peer_manager.list_peers()
    for peer in peers:
        connection.send_message(peer, "GET_PEERS", waitForAnswer=True)

def list_local_files():
    shared_dir = get_shared_dir()
    if not shared_dir:
        print("Erro: O diretório compartilhado não foi configurado.")
        return

    try:
        files = os.listdir(shared_dir)
        if files:
            for file in files:
                print(f"\t{file}")
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")

def search_files():
    peers = peer_manager.get_online_peers()
    if not peers:
        print("Nenhum peer online para buscar arquivos.")
        return
    connection.ls_results = [] # Limpa resultados de buscas anteriores
    for peer in peers:
        connection.send_message(peer, "LS", waitForAnswer=True)
    # Exibe menu de arquivos encontrados
    arquivos = {}
    for ip, port, files in connection.ls_results:
        for file_info in files:
            if ':' in file_info:
                nome, tamanho = file_info.split(":", 1)
            else:
                nome, tamanho = file_info, '0'
            tamanho = int(tamanho)
            arquivos.setdefault((nome, tamanho), []).append(f"{ip}:{port}")
    print("Arquivos encontrados na rede:")
    print("\t{:<4} {:<20} | {:<10} | {}".format('', 'Nome', 'Tamanho', 'Peer'))
    print("\t[ 0] {:<20} | {:<10} | {}".format('<Cancelar>', '', ''))
    
    keys = list(arquivos.keys())
    for idx, ((nome, tamanho), peers) in enumerate(arquivos.items(), start=1):
        print(f"\t[ {idx}] {nome:<20} | {tamanho:<10} | {', '.join(peers)}")
    
    print("\nDigite o numero do arquivo para fazer o download:")
    choice = int(input(">"))
    if choice == 0:
        return
    if choice < 1 or choice > len(arquivos):
        print("Escolha inválida.")
        return
    nome, tamanho = keys[choice - 1]
    peers = arquivos[(nome, tamanho)]
    print(f"arquivo escolhido {nome}")


    chunk_size = connection.get_chunk_size()
    chunks = (tamanho + chunk_size - 1) // chunk_size # Calcula o número de chunks
    next_chunk = 0
    index_lock = threading.Lock()  # Lock para controlar o acesso ao índice do chunk

    file_results = connection.get_file_results()
    file_results.clear()  # Limpa resultados de downloads anteriores

    def worker(peer_addr):
        nonlocal next_chunk
        peer_ip, peer_port = peer_addr.split(":")
        peer_port = int(peer_port)
        peer = peer_manager.get_peer(peer_ip, peer_port)
        while next_chunk < chunks:
            with index_lock:
                current_chunk = next_chunk
                next_chunk += 1
            connection.send_message(peer, "DL", nome, chunk_size, current_chunk, waitForAnswer=True)

    threads = [] # Lista para armazenar threads e finalizá-las depois
    for peer_addr in peers:
        t = threading.Thread(target=worker, args=(peer_addr,))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()
    
    file_results = connection.get_file_results()

    file_results.sort() # Ordena os resultados por chunk


    share_dir = get_shared_dir()

    file_path = os.path.join(share_dir, nome)
    try:
        with open(file_path, "wb") as f:
            for _, content in file_results:
                f.write(base64.b64decode(content))
    except Exception as e:
        print(f"Erro ao salvar arquivo {nome}: {e}")
    print(f"\nDownload do arquivo {nome} finalizado.")

def show_statistics():
    print("")
    #TODO: Implementation

def change_chunk_size():
    print("Digite novo tamanho do chunk:")
    new_size = int(input(">"))
    if new_size <= 0:
        print("Tamanho inválido. Deve ser um número positivo.")
        return
    connection.change_chunk_size(new_size)

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
    set_shared_dir(shared_dir)

def main():
    if len(sys.argv) != 4:
        print("Uso: ./eachare <endereço:porta> <vizinhos.txt> <diretorio_compartilhado>")
        sys.exit(1)

    address, port = sys.argv[1].split(':')
    peers_file = sys.argv[2]
    verify_shared_dir(sys.argv[3])

    global connection 
    connection = Connection(address, port, peer_manager)

    try:
        read_peers(peers_file, peer_manager)
        connection.start_server() # Após ler os peers, inicia o servidor, conforme a especificação
        menu()
    except RuntimeError as error:
        print(error)

if __name__ == '__main__':
    main()
