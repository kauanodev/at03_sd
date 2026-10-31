# AT03 - Calculadora Distribuída e Projeto MQTT

**Disciplina:** CKP7500 - Sistemas Distribuídos e Redes de Comunicação (SMD - UFC)
**Professores:** Windson Viana de Carvalho e Fernando Antonio Mota Trinta
**Aluno:** Kauan Xavier
**Repositório:** https://github.com/kauanodev/at03_sd

Atividade sobre paradigmas de comunicação em sistemas distribuídos: uma calculadora remota implementada com **Sockets**, **HTTP-REST** e **JSON-RPC**, e um sistema de monitoramento de temperatura com **MQTT** (Publish-Subscribe). Todo o código foi feito em **Python 3**, usando apenas a biblioteca padrão, exceto o MQTT, que usa `paho-mqtt`.

## Vídeo do projeto MQTT

Execução dos sensores simulados enviando dados, do serviço CAT calculando as médias e do serviço Alarms disparando alarmes:

**https://drive.google.com/drive/folders/104bS00IqTHhUKCQvfVCEYZtUI3WIbXCf?usp=sharing**

## Estrutura do repositório

```
.
├── parser.py              # Parser de expressões (compartilhado pelas calculadoras)
├── socket_servidor.py     # Calculadora via Sockets (servidor, porta 5000)
├── socket_cliente.py      # Calculadora via Sockets (cliente)
├── http_servidor.py       # Calculadora HTTP-REST (servidor, porta 8000)
├── http_cliente.py        # Calculadora HTTP-REST (cliente com política de Retry)
├── jsonrpc_servidor.py    # Calculadora JSON-RPC 2.0 (servidor, porta 4000)
├── jsonrpc_cliente.py     # Calculadora JSON-RPC 2.0 (cliente)
├── sensor.py              # MQTT: sensor de temperatura simulado
├── cat.py                 # MQTT: serviço Compute Average Temperature
├── alarms.py              # MQTT: serviço de alarmes
├── prints/                # Capturas do Wireshark
└── README.md
```

## Requisitos

- Python 3.10 ou superior
- Para o MQTT: broker **Mosquitto** e a biblioteca `paho-mqtt`

```bash
sudo apt install mosquitto mosquitto-clients python3-venv
python3 -m venv venv
source venv/bin/activate
pip install paho-mqtt
```

As calculadoras (Sockets, HTTP, JSON-RPC) não precisam de nenhuma dependência além do Python.

---

## 1. Calculadoras distribuídas

Todas as calculadoras suportam as operações **soma, subtração, multiplicação e divisão** (com tratamento de divisão por zero) e **expressões com parênteses**, como `(10 + 15) * 4`. O cliente tem interface textual: o usuário digita a expressão e o programa mostra o resultado pelas duas abordagens.

### Parser de expressões (`parser.py`)

Módulo único reaproveitado por todos os projetos. A função `avaliar(expr, executar)` interpreta a expressão (parser recursivo com precedência de operadores e parênteses) e chama a função `executar(op, a, b)` para cada operação:

- **No cliente**, `executar` faz uma **chamada remota** ao servidor.
- **No servidor**, `executar` é `calcular_local` e calcula localmente.

### Duas abordagens para expressões

| Abordagem | Como funciona | Chamadas ao servidor |
|---|---|---|
| **1 - Cliente decompõe** | O cliente interpreta a expressão e chama o servidor para cada operação básica | Várias (uma por operação) |
| **2 - Servidor calcula** | O cliente envia a expressão inteira e o servidor devolve o resultado | Uma |

### Sockets (porta 5000)

Protocolo de texto próprio sobre TCP:

- Operação: `OP;add;10;15`
- Expressão: `EXPR;(10+15)*4`
- Resposta: `OK;100.0` ou `ERRO;mensagem`

```bash
python3 socket_servidor.py     # terminal 1
python3 socket_cliente.py      # terminal 2
```

### HTTP-REST (porta 8000)

Servidor HTTP que recebe **POST** com os campos `op`, `a`, `b` (operação única) ou `expr` (expressão completa). Respostas: `200` em caso de sucesso e `400` em erro do cliente (ex.: divisão por zero).

**Política de Retry no cliente:**

- Até **4 tentativas**.
- **Backoff exponencial**: espera de 1s, 2s e 4s entre as tentativas.
- Repete apenas em falha de rede, timeout ou erro **5xx**.
- **Não** repete em erros **4xx**, pois repetir não mudaria o resultado.
- Cada tentativa é registrada no console.

```bash
python3 http_servidor.py       # terminal 1
python3 http_cliente.py        # terminal 2
```

Para testar o Retry, rode o cliente com o servidor desligado e observe as tentativas.

### JSON-RPC 2.0 (porta 4000)

Requisições no formato:

```json
{"jsonrpc": "2.0", "method": "subtract", "params": [10, 5], "id": 1}
```

Métodos: `add`, `subtract`, `multiply`, `divide` e `evaluate` (expressão completa). Erros voltam no campo `error` da resposta (ex.: `-32601` método inexistente, `-32000` erro de cálculo).

```bash
python3 jsonrpc_servidor.py    # terminal 1
python3 jsonrpc_cliente.py     # terminal 2
```

### RMI

**Não foi implementado** neste trabalho. A comparação do RMI no relatório é feita de forma teórica.

---

## 2. Projeto MQTT

Cenário: uma caldeira é monitorada por sensores de temperatura que publicam leituras em um broker MQTT. Dois serviços ligados ao broker processam os dados.

```
 Sensor 1 ─┐
 Sensor 2 ─┼──► Broker MQTT ──► CAT ──► (publica alertas) ──► Broker ──► Alarms
 Sensor N ─┘   (Mosquitto)
```

### Tópicos

| Tópico | Quem publica | Quem assina |
|---|---|---|
| `caldeira/temperatura/<id>` | Sensores | CAT (`caldeira/temperatura/+`) |
| `caldeira/alertas/aumento-repentino` | CAT | Alarms (`caldeira/alertas/#`) |
| `caldeira/alertas/temperatura-alta` | CAT | Alarms (`caldeira/alertas/#`) |

### Componentes

- **`sensor.py`**: sensor simulado. Publica uma temperatura a cada intervalo configurável (padrão 60s). O número de sensores é livre: basta iniciar mais instâncias com ids diferentes.
- **`cat.py`** (Compute Average Temperature): assina as temperaturas, guarda as leituras com timestamp, descarta as com mais de **120s** e calcula a média periodicamente. Publica:
  - **aumento repentino**, se as duas últimas médias diferem em **5 graus ou mais**;
  - **temperatura alta**, se a média passa de **200 graus**.
- **`alarms.py`**: assina `caldeira/alertas/#` e exibe cada alarme no console.

### Como executar

Com o broker Mosquitto rodando (`systemctl status mosquitto`), abra um terminal para cada comando, com o venv ativo (`source venv/bin/activate`):

```bash
python alarms.py                  # 1) serviço de alarmes
python cat.py 5                   # 2) CAT, calculando a média a cada 5s
python sensor.py 1 5              # 3) sensor 1, temperatura normal, a cada 5s
python sensor.py 2 5 250          # 4) sensor 2, base 250: dispara os alarmes
```

Parâmetros:

| Programa | Argumentos |
|---|---|
| `sensor.py` | `<id> <intervalo em s> <temperatura base>` (padrões: 1, 60, 100) |
| `cat.py` | `<período do cálculo em s>` (padrão 60) |

Os intervalos curtos (5s) servem para a demonstração. Os valores padrão (60s) seguem o enunciado.

---

## 3. Capturas de tráfego (Wireshark)

As capturas foram feitas na interface de loopback (`lo`), na pasta [`prints/`](prints/). Filtros usados:

| Tecnologia | Porta | Filtro |
|---|---|---|
| Sockets | 5000 | `tcp.port == 5000` |
| HTTP-REST | 8000 | `tcp.port == 8000` |
| JSON-RPC | 4000 | `tcp.port == 4000` |
| MQTT | 1883 | `mqtt` |

Nas capturas é possível ver: o texto do protocolo próprio nos sockets (`OP;add;10;15`), os POST do HTTP, o JSON das requisições do JSON-RPC e os pacotes CONNECT, SUBSCRIBE e PUBLISH do MQTT, com tópico e valor.

## 4. Comparação resumida dos modelos

| Critério | Sockets | HTTP-REST | JSON-RPC | MQTT |
|---|---|---|---|---|
| Modelo | Requisição-resposta | Requisição-resposta | Chamada remota de procedimento | Publish-Subscribe |
| Interoperabilidade | Baixa (protocolo próprio) | Alta | Alta | Alta (padrão OASIS) |
| Desacoplamento espacial | Não | Não | Não | **Sim** |
| Desacoplamento temporal | Não | Não | Não | **Sim** |
| Overhead | Muito baixo | Alto (cabeçalhos em texto) | Alto (HTTP + JSON) | Muito baixo |
| Cenário ideal | Comunicação simples e direta | APIs web | Chamadas de procedimento entre sistemas | IoT e eventos em larga escala |

## 5. Observações

- Todos os arquivos de comunicação estão comentados para explicar o que cada linha faz.
- O `parser.py` é reaproveitado pelas três calculadoras, evitando código duplicado.
- O broker Mosquitto roda localmente (`localhost:1883`), sem autenticação, apenas para fins didáticos.