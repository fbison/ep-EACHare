# EACHare - Arquitetura do Sistema

## Visão Geral

O EACHare é um sistema distribuído de compartilhamento de arquivos peer-to-peer que implementa os seguintes conceitos fundamentais de sistemas distribuídos:

- **Relógios Lógicos de Lamport**: Para ordenação de eventos
- **Protocolo de Comunicação P2P**: Baseado em TCP com mensagens estruturadas
- **Thread Safety**: Operações concorrentes seguras
- **Transferência Paralela**: Download de arquivos usando múltiplos peers

## Componentes Principais

### 1. `main.py` - Interface Principal
- **Responsabilidades**:
  - Menu interativo do usuário
  - Coordenação de downloads paralelos
  - Estatísticas de performance
  - Gerenciamento de chunks

- **Funcionalidades principais**:
  - `search_files()`: Busca arquivos na rede P2P
  - `download_chunks_worker()`: Worker thread para download paralelo
  - `add_download_statistics()`: Coleta métricas usando algoritmo de Welford
  - `show_statistics()`: Exibe estatísticas de throughput

### 2. `connection.py` - Gerenciamento de Conexões
- **Responsabilidades**:
  - Servidor TCP para aceitar conexões
  - Cliente TCP para enviar mensagens
  - Implementação do protocolo de mensagens
  - Gerenciamento de relógios lógicos

- **Padrões implementados**:
  - **Servidor multithread**: Cada conexão em thread separada
  - **Relógios Lógicos**: `increment_clock()` e `update_clock()`
  - **Protocol Handler**: `handle_message()` processa tipos de mensagem
  - **Thread Pool**: Gerenciamento automático de threads

### 3. `peer_manager.py` - Gerenciamento de Peers
- **Responsabilidades**:
  - Manutenção da tabela de peers
  - Descoberta de novos peers
  - Controle de status online/offline
  - Thread safety para operações concorrentes

- **Operações principais**:
  - `add_peer_with_details()`: Adiciona peer com informações completas
  - `get_online_peers()`: Filtra peers disponíveis
  - `handle_peers_list()`: Processa listas recebidas de outros peers

### 4. `peer.py` - Representação de Peer
- **Responsabilidades**:
  - Encapsulamento de dados do peer
  - Thread safety para acesso aos atributos
  - Serialização para protocolo de rede

- **Thread Safety**:
  - Lock individual por peer
  - Operações atômicas para mudança de estado
  - Proteção para relógio lógico

### 5. `utils.py` - Utilitários Thread-Safe
- **Responsabilidades**:
  - `print_with_lock()`: Função global para prints thread-safe
  - Inicialização lazy do lock para evitar problemas de importação

### 6. `config.py` - Configuração Global
- **Responsabilidades**:
  - Gerenciamento do diretório compartilhado
  - Configurações globais do sistema

## Protocolo de Comunicação

### Formato de Mensagens
```
<IP>:<PORTA> <CLOCK> <TIPO> [ARGUMENTOS]
```

### Tipos de Mensagem

| Tipo | Descrição | Argumentos | Resposta |
|------|-----------|------------|----------|
| `HELLO` | Saudação entre peers | - | - |
| `GET_PEERS` | Solicita lista de peers | - | `PEER_LIST` |
| `PEER_LIST` | Lista de peers conhecidos | `<count> <peer1> <peer2> ...` | - |
| `LS` | Lista arquivos disponíveis | - | `LS_LIST` |
| `LS_LIST` | Lista de arquivos | `<count> <file1:size> <file2:size> ...` | - |
| `DL` | Solicita chunk de arquivo | `<filename> <chunk_size> <chunk_index>` | `FILE` |
| `FILE` | Chunk de arquivo | `<filename> <size> <chunk_index> <base64_data>` | - |
| `BYE` | Notifica desconexão | - | - |

## Thread Safety

### Estratégias Implementadas

1. **Print Global Thread-Safe**:
   ```python
   # utils.py
   def print_with_lock(*args, **kwargs):
       if not hasattr(print_with_lock, "_lock"):
           print_with_lock._lock = threading.Lock()
       with print_with_lock._lock:
           print(*args, **kwargs)
   ```

2. **Locks por Peer**:
   ```python
   # peer.py
   class Peer:
       def __init__(self, ...):
           self.lock = threading.Lock()
       
       def set_clock(self, clock):
           with self.lock:
               self.clock = clock
   ```

3. **Lock para Relógio Lógico**:
   ```python
   # connection.py
   def increment_clock(self):
       with self.lock:
           self.clock += 1
   ```

4. **Lock para Resultados de Arquivo**:
   ```python
   # connection.py
   def handle_message(self, ...):
       if message_list[2] == "FILE":
           with self.file_results_lock:
               self.file_results.append((chunk_index, data))
   ```

## Download Paralelo

### Algoritmo de Distribuição de Chunks

```python
def download_chunks_worker(peer_addr):
    nonlocal next_chunk
    while next_chunk < chunks:
        with index_lock:  # Atomic chunk assignment
            current_chunk = next_chunk
            next_chunk += 1
        # Download chunk from peer
        connection.send_message(peer, "DL", filename, chunk_size, current_chunk)
```

### Características:
- **Balanceamento automático**: Chunks distribuídos dinamicamente
- **Fault tolerance**: Falha de peer não afeta outros downloads
- **Reassembly**: Chunks ordenados e reassemblados automaticamente

## Métricas e Estatísticas

### Algoritmo de Welford para Cálculo Online
- **Média móvel**: Atualizada incrementalmente
- **Desvio padrão**: Calculado sem armazenar todos os valores
- **Agrupamento**: Por (chunk_size, num_peers, file_size)

```python
# Welford online algorithm
n += 1
delta = download_time - mean
mean += delta / n
delta2 = download_time - mean
M2 += delta * delta2
stddev = sqrt(M2 / (n - 1))
```

## Considerações de Design

### Decisões Arquiteturais

1. **TCP vs UDP**: TCP escolhido para garantir entrega confiável
2. **Threads vs Async**: Threads para simplicidade e compatibilidade
3. **Base64 encoding**: Para transmissão segura de dados binários
4. **Chunk-based transfer**: Para paralelização e fault tolerance

## Testes

### Cenários de Teste Implementados

1. **`test_peer_manager.py`**: Gerenciamento de peers
2. **`test_abbreviate_message.py`**: Formatação de mensagens
3. **`test_show_statistics.py`**: Exibição de estatísticas

### Tipos de Teste

- **Unit tests**: Componentes individuais
- **Integration tests**: Interação entre componentes
- **Thread safety tests**: Condições de corrida