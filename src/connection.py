import socket
import threading
from peer import Peer

MAX_CONNECTIONS = int(5)

class Connection:
    def __init__(self, address, port):
        self.address = address
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #socket.AF_INET define o uso de protocolos IPv4
        #socket.SOCK_STREAM define o uso de TCP
        self.running = True  # Controle da execução

    def start_server(self):
        self.socket.bind((self.address, self.port))
        self.socket.listen(MAX_CONNECTIONS)  # Máximo de conexões na fila
        #TODO Retirar esse print após testes
        print(f"Peer ativo em {self.address}:{self.port}")

        # Inicia um thread daemos para aceitar conexões,
        # elas são executadas em segundo plano e não bloqueiam o programa ser finalizado
        thread = threading.Thread(target=self.accept_connections, daemon=True)
        thread.start()

    def accept_connections(self):
        """Aceita conexões de outros peers e gerencia as requisições."""
        while self.running:
            try:
                client_socket, client_address = self.socket.accept() 
                #self.socket.accept() Bloqueia a execução da thread até receber uma conexão
                print(f"Conexão recebida de {client_address}")

                # Inicia um thread para tratar essa conexão
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.start()
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
                print(f"Recebido: {data}")
                client_socket.send("ACK".encode())  # Responde com um ACK
        except Exception as e:
            print(f"Erro ao lidar com cliente: {e}")
        finally:
            client_socket.close()

    def connect_to_peer(self, peer: Peer):
        """Conecta-se a um peer para trocar informações."""
        try:
            with socket.create_connection((peer.ip, int(peer.port))) as peer_socket:
                #TODO Verificar com o professor sobre deixar a conexão aberta após receber um HELLO,
                #     ou se é para fechar a conexão após receber a resposta
                peer_socket.send("HELLO".encode())
                #TODO Formatar a função corretamente, vale a pena criar uma função que faz isso e envia as mensagens
                # facilitando até pra concentrar a impressão de logs em um só lugar	
                response = peer_socket.recv(1024).decode()
                print(f"Resposta do peer {peer.ip}:{peer.port} -> {response}")
        except Exception as e:
            print(f"Erro ao conectar com peer {peer.ip}:{peer.port}: {e}")

    def stop(self):
        self.running = False
        self.socket.close()
        print("Servidor encerrado.")
