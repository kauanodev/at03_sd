import urllib.request, json                                   # só biblioteca padrão
from parser import avaliar                                    # parser para a abordagem 1

URL = "http://localhost:4000/"                                # endereço do servidor
contador = [0]                                                # gera o id de cada requisição

def chamar(metodo, params):                                   # faz uma chamada JSON-RPC
    contador[0] += 1                                          # novo id
    corpo = json.dumps({"jsonrpc": "2.0", "method": metodo,
                        "params": params, "id": contador[0]}).encode()   # monta a requisição
    req = urllib.request.Request(URL, corpo, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=3) as r:         # envia
        resp = json.loads(r.read().decode())                  # lê a resposta
    if "error" in resp:                                       # trata erro retornado
        raise ValueError(resp["error"]["message"])
    return resp["result"]

NOMES = {"add": "add", "sub": "subtract", "mul": "multiply", "div": "divide"}

def remoto(op, a, b):                                         # operação remota usada pelo parser
    return chamar(NOMES[op], [a, b])

while True:                                                   # interface textual
    expr = input("Expressão (ou 'sair'): ")
    if expr == "sair":
        break
    try:
        print("Abordagem 1:", avaliar(expr, remoto))          # cliente decompõe
        print("Abordagem 2:", chamar("evaluate", [expr]))     # servidor calcula
    except Exception as e:
        print("Erro:", e)
