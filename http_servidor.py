from http.server import BaseHTTPRequestHandler, HTTPServer   # servidor HTTP padrão
from urllib.parse import parse_qs                             # lê o corpo do POST
from parser import avaliar, calcular_local                    # nosso parser

class H(BaseHTTPRequestHandler):                              # trata as requisições
    def do_POST(self):                                        # método chamado a cada POST
        n = int(self.headers.get("Content-Length", 0))        # tamanho do corpo
        d = parse_qs(self.rfile.read(n).decode())             # campos do formulário
        try:
            if "expr" in d:                                   # modo expressão completa
                res = avaliar(d["expr"][0], calcular_local)   # servidor calcula tudo
            else:                                             # modo operação única
                res = calcular_local(d["op"][0], float(d["a"][0]), float(d["b"][0]))
            self.send_response(200); corpo = str(res)         # sucesso
        except Exception as e:
            self.send_response(400); corpo = str(e)           # erro do cliente (4xx)
        self.end_headers()                                    # encerra os cabeçalhos
        self.wfile.write(corpo.encode())                      # envia a resposta

HTTPServer(("0.0.0.0", 8000), H).serve_forever()              # sobe na porta 8000
