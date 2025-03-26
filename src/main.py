import sys
from collections import OrderedDict

# Exit constant
EXIT_COMMAND = '9'

def list_peers():
    #TODO: Implementation

commands_functions = OrderedDict([ # OrderedDict to keep the order of insertion
    ("Listar peers", list_peers)
    #TODO: Add the other commands
])

def show_commands():
    print("Escolha um comando:")


def main():
    address, port = sys.argv[1].split(':')
    peers_file = sys.argv[2]
    shared_dir = sys.argv[3]

    show_commands()

if __name__ == '__main__':
    main()
