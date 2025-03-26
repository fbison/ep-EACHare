from peer import Peer

class PeerManager:
    def __init__(self):
        self.peers = {}

    def add_peer(self, ip, port):
        self.peers[(ip, port)] = Peer(ip, port)

    #TODO: Verificar se vale a pena essa função ser responsável pela impressão do menu, 
    #ou deixamos ela só retornar a lista de peers e outra função cuidar da lógica desse menu

    #TODO: Verificar se o menu de peers fica iterando até a pessoa sair ou após mandar um HELLO ele retorna
    def list_peers(self):
        print("\t [0] voltar para o menu anterior")
        for index, peer in enumerate(self.peers.values(), start=1):
            print(f"\t [{index}] {peer.ip}:{peer.port} {'ONLINE' if peer.online else 'OFFLINE'}")
        command_number = int(input(">"))
        if command_number == 0:
            return
        if command_number > len(self.peers):
            print("Por favor, insira um número válido.")
            return
        print("enviar hello para: \n")
        #TODO Arrumar um lugar melhor para não criar mais dependencia para a classe Peer com a classe connection que faz o helo
        print(list(self.peers.values())[command_number - 1])


    def get_online_peers(self):
        return [peer for peer in self.peers.values() if peer.online]