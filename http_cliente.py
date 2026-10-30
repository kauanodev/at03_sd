import urllib.request, urllib.parse, urllib.error, time       # só biblioteca padrão
from parser import avaliar                                    # parser para a abordagem 1

URL = "http://localhost:8000/"                                # endereço do servidor
TENTATIVAS = 4                                                # máximo de tentativas
ESPERA = 1                                                    # espera inicial (s)

def post(dados):                                              # POST com política de Retry
    corpo = urllib.parse.urlencode(dados).encode()            # codifica o formulário
    espera = ESPERA                                           # espera atual
    for t in range(1, TENTATIVAS + 1):                        # tenta até N vezes
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, corpo), timeout=3) as r:
                return r.read().decode()                      # sucesso
        except urllib.error.HTTPError as e:
            if e.code < 500:                                  # 4xx: não adianta repetir
                raise ValueError(e.read().decode())
            print(f"Tentativa {t} falhou (HTTP {e.code})")    # 5xx: repete
        except Exception as e:
            print(f"Tentativa {t} falhou ({e})")              # rede/timeout: repete
        if t < TENTATIVAS:                                    # ainda há tentativas
            print(f"Aguardando {espera}s para tentar de novo...")
            time.sleep(espera)                                # espera antes de repetir
            espera *= 2                                       # backoff: 1s, 2s, 4s
    raise ConnectionError("Servidor indisponível após todas as tentativas")

def remoto(op, a, b):                                         # uma operação remota
    return float(post({"op": op, "a": a, "b": b}))

while True:                                                   # interface textual
    expr = input("Expressão (ou 'sair'): ")
    if expr == "sair":
        break
    try:
        print("Abordagem 1:", avaliar(expr, remoto))          # cliente decompõe
        print("Abordagem 2:", post({"expr": expr}))           # servidor calcula
    except Exception as e:
        print("Erro:", e)
