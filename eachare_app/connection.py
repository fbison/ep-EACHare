import socket
import threading
import os  # Corrigido: import os no topo
import base64  # Corrigido: import base64 no topo

from eachare_app.peer import Peer
from eachare_app.peer_manager import PeerManager
from eachare_app.config import get_shared_dir

MAX_CONNECTIONS = int(5)
TIMEOUT_CONNECTION = int(5) # Diminui o tempo de espera para uma conexão offline
#TODO Tem uma forma de configurar ele global pra biblioteca do socket,
# mas não estava conseguindo então passei por param na conexão
class Connection:
    def __init__(self, address, port, peer_manager: PeerManager):
        self.address = address
        self.port = int(port)
        self.peer_manager = peer_manager
        self.running = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #socket.AF_INET define o uso de protocolos IPv4
        #socket.SOCK_STREAM define o uso de TCP
        self.chunk_size = 256
        self.clock = 0
        self.lock = threading.Lock() # Cria um lock para controlar o acesso ao clock
        self.ls_results = []  # Guarda resultados LS_LIST
        self.file_results = []  # Guarda resultados FILE
        self.file_results_lock = threading.Lock()  # Lock para controlar o acesso à lista do FILE
        self.print_lock = threading.Lock()  # Lock para prints thread-safe

    def start_server(self):
        self.socket.bind((self.address, self.port))  
        self.socket.listen(MAX_CONNECTIONS)  # Máximo de conexões na fila
        self.running = True  # Controle da execução

        # Inicia um thread daemon para aceitar conexões,
        # elas são executadas em segundo plano e não bloqueiam o programa ser finalizado
        thread = threading.Thread(target=self.accept_connections, daemon=True)
        thread.start()

    def accept_connections(self):
        """Aceita conexões de outros peers e gerencia as requisições."""
        while self.running:
            try:
                client_socket, _ = self.socket.accept() 
                #self.socket.accept() Bloqueia a execução da thread até receber uma conexão
                # Inicia um thread para tratar essa conexão
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.start()
            except Exception as e:
                if self.running:  # Apenas imprime o erro se o servidor ainda estiver rodando
                    print(f"Erro ao aceitar conexão: {e}")

    def handle_client(self, client_socket):
        """Lida com mensagens recebidas de um peer."""
        try:
            buffer = ""
            while True:
                chunk = client_socket.recv(1024).decode()
                if not chunk:
                    # Conexão foi encerrada pelo peer antes de chegar o \n, ou seja, não é uma mensagem completa
                    break
                buffer += chunk
                if '\n' in buffer:
                    message = buffer.split('\n', 1)[0]  # Verifica que a mensagem é finalizada no \n
                    self.handle_message(message.strip(), client_socket)
                    #Impede que chegue no finally e feche o socket antes de enviar a resposta
                    #Será fechada por quem recebeu a conexão
                    return 
        except Exception as e:
            print(f"Erro ao lidar com cliente: {e} (type: {type(e)})")
            client_socket.close()
       
    def format_message(self, message_type: str, *args) -> str:
        args_str =" " + " ".join(map(str, args)) if args else ""
        return f"{self.address}:{self.port} {self.clock} {message_type}{args_str}\n"

    def increment_clock(self):
        """Incrementa o relógio lógico."""
        with self.lock:
            self.clock += 1
            print(f"\t=> Atualizando relogio para {self.clock}")

    
    def update_clock(self, peer_clock:int):
        """Atualiza o relógio lógico com o valor do peer."""
        with self.lock:
            self.clock = max(self.clock, peer_clock) + 1
            print(f"\t=> Atualizando relogio para {self.clock}")
    
    def get_chunk_size(self) -> int:
        """Retorna o tamanho do chunk usado nos downloads."""
        return self.chunk_size

    def change_chunk_size(self, new_size: int):
        """Altera o tamanho do chunk usado nos downloads."""
        if new_size <= 0:
            raise ValueError("O tamanho do chunk deve ser maior que zero.")
        self.chunk_size = new_size
        print("\tTamanho do chunk alterado:", self.chunk_size)

    def get_file_results(self):
        """Retorna os resultados de arquivos recebidos."""
        return self.file_results

    def get_peers_response_args(self, peer_ip, peer_port):
        # Verifica se o peer já existe, se não existir adiciona
        try:
            peer = self.peer_manager.get_peer(peer_ip, peer_port)
        except KeyError:
            self.peer_manager.add_peer(peer_ip, peer_port)
            peer = self.peer_manager.get_peer(peer_ip, peer_port)
        list_message = self.peer_manager.list_peers_message(peer)
        num_peers_message = len(list_message.split(" "))
        return peer, num_peers_message, list_message
    
    message_type = {
        "HELLO", "PEER_LIST", "GET_PEERS", "BYE", "LS", "LS_LIST", "DL", "FILE"
    }
    response_type = {"PEER_LIST", "LS_LIST", "FILE"}

    def handle_message(self, message:str, client_socket:socket.socket):
        message = message.strip()
        message_list = message.split(" ")
        peer_ip, peer_port = message_list[0].split(":")
        peer_port = int(peer_port)
        clock = int(message_list[1])

        if message_list[2] not in self.message_type:
            print(f"\tMensagem desconhecida: \"{message}\"")
            return
        
        # Atualiza o clock do peer que enviou a mensagem
        try:
            peer = self.peer_manager.get_peer(peer_ip, peer_port)
        except KeyError:
            self.peer_manager.add_peer(peer_ip, peer_port)
            peer = self.peer_manager.get_peer(peer_ip, peer_port)
        peer.set_online()
        if clock > peer.clock:
            peer.set_clock(clock)

        # Impressão de acordo com o tipo de mensagem
        if message_list[2] in self.response_type:
            print(f"\tResposta recebida: \"{message}\"")
        else:
            print(f"\tMensagem recebida: \"{message}\"")
        # Atualiza o relógio lógico com o valor do peer
        self.update_clock(clock)

        # Trata Respostas
        if message_list[2] == "PEER_LIST":
            self.peer_manager.handle_peers_list(message_list, self.address, self.port)
            return
        if message_list[2] == "LS_LIST":
            self.ls_results.append((peer_ip, peer_port, message_list[4:]))
            return
        if message_list[2] == "DL":
            share_dir = get_shared_dir()
            file_name = message_list[3]
            chunk_size = int(message_list[4])
            chunk_index = int(message_list[5])
            file_path = os.path.join(share_dir, file_name)
            try:
                with open(file_path, "rb") as f:
                    f.seek(chunk_index * chunk_size)
                    chunk_data = f.read(chunk_size)
                encoded_content = base64.b64encode(chunk_data).decode("utf-8")
            except Exception as e:
                encoded_content = ""
            self.send_answer(peer, client_socket, "FILE", file_name, len(chunk_data), chunk_index, encoded_content)
            return
        if message_list[2] == "FILE":
            with self.file_results_lock:
                self.file_results.append((message_list[5], message_list[6])) # Armazena o índice do chunk e o arquivo encoded
        # Trata Requisições
        if message_list[2] == "LS":
            share_dir = get_shared_dir()
            list_message = " ".join([f"{file}:{os.path.getsize(os.path.join(share_dir, file))}" for file in os.listdir(share_dir)])
            num_files_message = len(list_message.split(" ")) if list_message else 0
            self.send_answer(peer, client_socket, "LS_LIST", num_files_message, list_message)
            return
        if message_list[2] == "GET_PEERS":
            peer, num_peers_message, list_message = self.get_peers_response_args(peer_ip, peer_port)
            self.send_answer(peer, client_socket, "PEER_LIST", num_peers_message, list_message)
            return
        client_socket.close() # Como as mensagens abaixo não tem resposta, fecha o socket
        if message_list[2] == "HELLO":
            return
        if message_list[2] == "BYE":
            peer.set_offline()
            
    def receive_response(self, sock):
        buffer = ""
        while True:
            chunk = sock.recv(1024).decode()
            if not chunk:
                break
            buffer += chunk
            if '\n' in buffer:
                break
        return buffer.strip()

    def send_message(self, peer: Peer, type: str, *args, waitForAnswer:bool = False): 
        #Conecta-se com um peer para o envio de uma mensagem, toda mensagem cria uma nova conexão
        peer_socket = None  # Inicializa como None para evitar problemas se a conexão falhar
        try:
            peer_socket = socket.create_connection((peer.ip, int(peer.port)), timeout=TIMEOUT_CONNECTION)
            self.increment_clock()
            message = self.format_message(type, *args)
            with self.print_lock:
                print(f"\tEncaminhando mensagem \"{message.strip()}\" para {peer.ip}:{peer.port}")
            peer_socket.sendall(message.encode())
            peer.set_online()

            if waitForAnswer:
                response = self.receive_response(peer_socket)
                self.handle_message(response, peer_socket)

        except Exception as e:
            with self.print_lock:
                print(f"Erro ao conectar com peer {peer.ip}:{peer.port}: {e}")
            peer.set_offline()

        finally:
            if peer_socket:
                peer_socket.close()
    
    def send_answer(self, peer: Peer, client_socket: socket.socket, type: str, *args):
        #Envia uma mensagem pela conexão já estabelecida (resposta direta)
        try:
            self.increment_clock()
            message = self.format_message(type, *args)
            with self.print_lock:
                print(f"\tEncaminhando mensagem \"{message.strip()}\" para {peer.ip}:{peer.port}")
            client_socket.sendall(message.encode())
        except Exception as e:
            with self.print_lock:
                print(f"Erro ao conectar com peer {peer.ip}:{peer.port}: {e}")
            peer.set_offline()
        finally:
            client_socket.close()
            # Fecha o socket após enviar a resposta, pois não é mais necessária a conexão

    def stop(self):
        self.running = False
        self.socket.close()
        print("Saindo...")
