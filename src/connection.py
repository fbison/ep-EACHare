import socket
import threading
from peer import Peer
from peer_manager import PeerManager

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
        self.threads = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #socket.AF_INET define o uso de protocolos IPv4
        #socket.SOCK_STREAM define o uso de TCP
        self.clock = 0

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
                client_socket, client_address = self.socket.accept() 
                #self.socket.accept() Bloqueia a execução da thread até receber uma conexão
                print(f"Conexão recebida de {client_address}") #TODO Retirar esse print após testes

                # Inicia um thread para tratar essa conexão
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.start()
                self.threads.append(thread)
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")

    def handle_client(self, client_socket):
        """Lida com mensagens recebidas de um peer."""
        try:
            while self.running:
                data = client_socket.recv(1024).decode()
                if not data:
                    #TODO adicionar um handle message que trata todo tipo de mensagem
                    break
                self.handle_message(data)
        except Exception as e:
            print(f"Erro ao lidar com cliente: {e}")
        finally:
            client_socket.close()

    #Usar isso pra handle message
    message_type = {
        "HELLO","PEER_LIST", "GET_PEERS", "BYE"
    }
    
    def handle_peers_list(self, message:list):
        """Lida com a lista de peers recebida de um peer."""
        peers_list = message[4:]
        for peer in peers_list:
            peer_data = peer.split(":")
            port = int(peer_data[1])
            if(self.address == peer_data[0] and self.port == port):
                continue
            status = True if peer_data[3] == "ONLINE" else False
            self.peer_manager.add_peer_with_details(peer_data[0], port, status, peer_data[3])

    def format_message(self, message_type: str, *args) -> str:
        args_str =" " + " ".join(map(str, args)) if args else ""
        return f"{self.address}:{self.port} {self.clock} {message_type}{args_str}\n"

    def increment_clock(self):
        """Incrementa o relógio lógico."""
        self.clock += 1
        print(f"=> Atualizando relógio para {self.clock}")
    
    def handle_message(self, message:str):
        message = message.strip()
        print(f"Resposta Recebida: {message}")
        self.increment_clock()
        message = message.split(" ")
        peer_ip, peer_port = message[0].split(":")
        print(message)
        if message[2] == "HELLO":
            self.peer_manager.add_online_peer(peer_ip, peer_port)
        elif message[2] == "PEER_LIST":
            self.handle_peers_list(message)
        elif message[2] == "GET_PEERS":
            self.peer_manager.add_online_peer(peer_ip, peer_port) # TODO: verificar se tem que fazer isso mesmo
            peer = self.peer_manager.get_peer(peer_ip, peer_port)
            list_message = self.peer_manager.list_peers_message(peer)
            num_peers_message = len(list_message.split(" "))
            self.send_message(peer, 
                              "PEER_LIST", num_peers_message,
                              list_message)
        elif message[2] == "BYE":
            self.peer_manager.get_peer(peer_ip, peer_port).set_offline()
        else:
            print("Mensagem desconhecida")

    def send_message(self, peer: Peer, type: str, *args): #TODO verificar se type não é uma palavra reservada
        #Conecta-se com um peer para o envio de uma mensagem, toda mensagem cria uma nova conexão
        try:
            with socket.create_connection((peer.ip, int(peer.port)), timeout=TIMEOUT_CONNECTION) as peer_socket:
                #TODO Verificar com o professor sobre deixar a conexão aberta após receber um HELLO,
                #     ou se é para fechar a conexão após receber a resposta como está sendo feito
                print(type)
                print(args)
                self.increment_clock()
                message=self.format_message(type, *args)
                print(f"Encaminhando mensagem \"{message.strip()}\" para {peer.ip}:{peer.port}")
                peer_socket.send(message.encode())
                peer.set_online()
                #TODO Verificar se é necessário fechar a conexão após receber a resposta
        except Exception as e:
            print(f"Erro ao conectar com peer {peer.ip}:{peer.port}: {e}")
            peer.set_offline()

    def stop(self):
        self.running = False
        self.socket.close()
        for thread in self.threads:
            thread.join() # Espera as threads terminarem
        print("Saindo...")
