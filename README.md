# EACHare

EACHare é um sistema de compartilhamento de arquivos peer-to-peer implementado em Python. O sistema utiliza relógios lógicos, gerenciamento robusto de peers, transferência de arquivos com base64 e chunks, e interface thread-safe.

## Características

- **Gerenciamento de Peers**: Sistema robusto de descoberta e manutenção de peers com status online/offline
- **Relógios Lógicos**: Implementação de relógios lógicos de Lamport para ordenação de eventos
- **Transferência de Arquivos**: 
  - Download paralelo com chunks
  - Codificação/decodificação base64
  - Suporte a múltiplos peers simultâneos
- **Thread Safety**: Todas as operações de I/O e print são thread-safe
- **Interface de Usuário**: Menu interativo para listagem, busca e download de arquivos

## Requisitos
- **Python 3.10.12 ou superior**

## Estrutura do Projeto

```
eachare_app/
├── __init__.py
├── config.py          # Configuração do diretório compartilhado
├── connection.py      # Gerenciamento de conexões TCP e protocolo
├── main.py            # Interface principal e lógica de download
├── peer.py            # Classe Peer com thread safety
├── peer_manager.py    # Gerenciamento da tabela de peers
└── utils.py           # Utilitários thread-safe (print_with_lock)
```

## Como executar

No diretório `ep-EACHare`, execute o seguinte comando:
```bash
./eachare <endereco>:<porta> <vizinhos.txt> <diretorio_compartilhado>
```

### Exemplo:
```bash
./eachare 127.0.0.1:8080 vizinhos8080.txt shared8080
```

Se necessário, configure o arquivo `eachare` como executável:
```bash
chmod +x eachare
```

## Funcionalidades

1. **Listar peers**: Visualiza todos os peers conhecidos e seus status
2. **Obter peers**: Solicita lista de peers de outros nós da rede
3. **Listar arquivos locais**: Mostra arquivos no diretório compartilhado
4. **Buscar arquivos**: Procura arquivos disponíveis na rede
5. **Download de arquivos**: Download paralelo com múltiplos peers
6. **Estatísticas**: Visualiza estatísticas de download (tempo, throughput)
7. **Configurar chunk size**: Ajusta o tamanho dos chunks para download

## Protocolo de Mensagens

- `HELLO`: Saudação entre peers
- `GET_PEERS`: Solicita lista de peers
- `PEER_LIST`: Resposta com lista de peers
- `LS`: Lista arquivos disponíveis
- `LS_LIST`: Resposta com lista de arquivos
- `DL`: Solicita download de chunk específico
- `FILE`: Resposta com chunk do arquivo
- `BYE`: Notifica desconexão

## Thread Safety

O sistema implementa thread safety em todas as operações críticas:
- Prints utilizando `print_with_lock()` global
- Acesso a relógios lógicos protegido por locks
- Operações em peers protegidas por locks individuais
- Lista de resultados de arquivo protegida por locks