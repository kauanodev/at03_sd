import socket                      # biblioteca de sockets
from parser import avaliar, calcular_local   # nosso parser

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket TCP
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # permite reiniciar rápido
s.bind(("0.0.0.0", 5000))          # associa à porta 5000
s.listen()                         # aguarda conexões
print("Servidor de sockets na porta 5000")

while True:                        # atende clientes continuamente
    conn, addr = s.accept()        # aceita uma conexão
    with conn:
        linha = conn.recv(1024).decode().strip()   # lê a requisição
        try:
            partes = linha.split(";")              # protocolo: OP;add;10;15 ou EXPR;(10+15)*4
            if partes[0] == "OP":
                res = calcular_local(partes[1], float(partes[2]), float(partes[3]))
            elif partes[0] == "EXPR":
                res = avaliar(partes[1], calcular_local)   # expressão inteira no servidor
            else:
                raise ValueError("Comando inválido")
            conn.sendall(f"OK;{res}".encode())     # resposta de sucesso
        except Exception as e:
            conn.sendall(f"ERRO;{e}".encode())     # resposta de erro
