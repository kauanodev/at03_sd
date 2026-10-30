from http.server import BaseHTTPRequestHandler, HTTPServer   # servidor HTTP padrão
import json                                                   # lê e escreve JSON
from parser import avaliar, calcular_local                    # nosso parser

# mapeia o nome do método JSON-RPC para a operação interna
METODOS = {"add": "add", "subtract": "sub", "multiply": "mul", "divide": "div"}

class H(BaseHTTPRequestHandler):                              # trata as requisições
    def do_POST(self):                                        # JSON-RPC usa POST
        n = int(self.headers.get("Content-Length", 0))        # tamanho do corpo
        req = json.loads(self.rfile.read(n).decode())         # converte o corpo em dicionário
        resp = {"jsonrpc": "2.0", "id": req.get("id")}        # monta a base da resposta
        try:
            m, p = req["method"], req.get("params", [])       # método e parâmetros
            if m in METODOS:                                  # operação básica
                resp["result"] = calcular_local(METODOS[m], float(p[0]), float(p[1]))
            elif m == "evaluate":                             # expressão inteira
                resp["result"] = avaliar(p[0], calcular_local)
            else:                                             # método inexistente
                resp["error"] = {"code": -32601, "message": "Method not found"}
        except Exception as e:                                # qualquer falha vira erro JSON-RPC
            resp["error"] = {"code": -32000, "message": str(e)}
        corpo = json.dumps(resp).encode()                     # serializa a resposta
        self.send_response(200)                               # HTTP 200 sempre
        self.send_header("Content-Type", "application/json")  # tipo do conteúdo
        self.end_headers()                                    # fim dos cabeçalhos
        self.wfile.write(corpo)                               # envia a resposta

HTTPServer(("0.0.0.0", 4000), H).serve_forever()              # porta 4000
