import socket                      # biblioteca de sockets
from parser import avaliar         # parser para o modo "cliente decompõe"

def enviar(msg):
    with socket.create_connection(("localhost", 5000)) as s:   # conecta ao servidor
        s.sendall(msg.encode())                                # envia a requisição
        return s.recv(1024).decode()                           # lê a resposta

def remoto(op, a, b):
    r = enviar(f"OP;{op};{a};{b}").split(";", 1)   # chamada remota de uma operação
    if r[0] != "OK":
        raise ValueError(r[1])
    return float(r[1])

while True:
    expr = input("Expressão (ou 'sair'): ")        # interface textual
    if expr == "sair":
        break
    try:
        print("Abordagem 1 (cliente decompõe):", avaliar(expr, remoto))   # várias chamadas
        print("Abordagem 2 (servidor calcula):", enviar(f"EXPR;{expr}"))  # uma chamada
    except Exception as e:
        print("Erro:", e)
