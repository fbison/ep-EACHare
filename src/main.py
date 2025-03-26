import sys
from collections import OrderedDict

# Exit constant
EXIT_COMMAND = 9

def list_peers():
    print("")
    #TODO: Implementation

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
    #TODO: Implementation

commands_functions = {
    1: {"description": "Listar peers", "function": list_peers},
    2: {"description": "Obter peers", "function": get_peers},
    3: {"description": "Listar arquivos locais", "function": list_local_files},
    4: {"description": "Buscar arquivos", "function": search_files},
    5: {"description": "Exibir estatisticas", "function": show_statistics},
    6: {"description": "Alterar tamanho de chunk", "function": change_chunk_size},
    EXIT_COMMAND: {"description": "Sair", "function": exit}
}


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



def main():
    address, port = sys.argv[1].split(':')
    peers_file = sys.argv[2]
    shared_dir = sys.argv[3]

    menu()

if __name__ == '__main__':
    main()
