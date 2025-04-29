import socket
import threading

from eachare_app.peer import Peer
from eachare_app.peer_manager import PeerManager

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
        self.clock = 0
        self.lock = threading.Lock() # Cria um lock para controlar o acesso ao clock

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
            print(f"Erro ao lidar com cliente: {e}")
            #TODO REMOVER LOG
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

    def get_peers_response_args(self, peer_ip, peer_port):
        peer = self.peer_manager.get_peer(peer_ip, peer_port)
        list_message = self.peer_manager.list_peers_message(peer)
        num_peers_message = len(list_message.split(" "))
        return peer, num_peers_message, list_message
    
    message_type = {
        "HELLO","PEER_LIST", "GET_PEERS", "BYE"
    }

    def handle_message(self, message:str, client_socket:socket.socket):
        message = message.strip()
        message_list = message.split(" ")
        peer_ip, peer_port = message_list[0].split(":")
        peer_port = int(peer_port)

        if message_list[2] not in self.message_type:
            print(f"\tMensagem desconhecida: \"{message}\"")
            return
        
        # Atualiza o relógio lógico com o valor do peer

        self.update_clock(int(message_list[1]))

        # Trata Respostas
        if message_list[2] == "PEER_LIST":
            print(f"\tResposta recebida: \"{message}\"")
            self.peer_manager.handle_peers_list(message_list, self.address, self.port)
            return
        
        # Trata Requisições
        print(f"\tMensagem recebida: \"{message}\"")

        if message_list[2] == "GET_PEERS":
            self.peer_manager.add_online_peer(peer_ip, peer_port)
            peer, num_peers_message, list_message = self.get_peers_response_args(peer_ip, peer_port)
            self.send_answer(peer, client_socket, "PEER_LIST", num_peers_message, list_message)
            return
        
        client_socket.close() # Como as mensagens abaixo não tem resposta, fecha o socket

        if message_list[2] == "HELLO":
            self.peer_manager.add_online_peer(peer_ip, peer_port)
            return
        
        
        if message_list[2] == "BYE":
            self.peer_manager.get_peer(peer_ip, peer_port).set_offline()
            
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
            print(f"\tEncaminhando mensagem \"{message.strip()}\" para {peer.ip}:{peer.port}")
            peer_socket.sendall(message.encode())
            peer.set_online()

            if waitForAnswer:
                response = self.receive_response(peer_socket)
                self.handle_message(response, peer_socket)

        except Exception as e:
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
            print(f"\tEncaminhando mensagem \"{message.strip()}\" para {peer.ip}:{peer.port}")
            client_socket.sendall(message.encode())
        except Exception as e:
            print(f"Erro ao conectar com peer {peer.ip}:{peer.port}: {e}")
            peer.set_offline()
        finally:
            client_socket.close()
            
            # Fecha o socket após enviar a resposta, pois não é mais necessária a conexão

    def stop(self):
        self.running = False
        self.socket.close()
        print("Saindo...")
