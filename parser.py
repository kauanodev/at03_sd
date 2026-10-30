import re                          # expressões regulares para separar os tokens

def tokenizar(expr):
    # separa números (inclusive decimais) e os símbolos + - * / ( )
    return re.findall(r"\d+\.?\d*|[+\-*/()]", expr.replace(" ", ""))

def avaliar(expr, executar):
    tokens = tokenizar(expr)       # lista de tokens da expressão
    pos = [0]                      # posição atual (lista para ser alterável nas funções internas)

    def olhar():
        return tokens[pos[0]] if pos[0] < len(tokens) else None  # token atual sem consumir

    def consumir():
        t = olhar()                # pega o token atual
        pos[0] += 1                # avança para o próximo
        return t

    def fator():
        t = consumir()             # lê o próximo token
        if t is None:
            raise ValueError("Expressão incompleta")
        if t == "(":               # parênteses: avalia o que está dentro
            v = soma()
            if consumir() != ")":
                raise ValueError("Parêntese não fechado")
            return v
        if t == "-":               # número negativo (ex.: -5)
            return executar("sub", 0, fator())
        return float(t)            # número comum

    def termo():
        v = fator()                # primeiro fator
        while olhar() in ("*", "/"):   # multiplicação e divisão têm prioridade
            op = consumir()
            d = fator()
            v = executar("mul" if op == "*" else "div", v, d)  # chamada da operação
        return v

    def soma():
        v = termo()                # primeiro termo
        while olhar() in ("+", "-"):   # soma e subtração
            op = consumir()
            d = termo()
            v = executar("add" if op == "+" else "sub", v, d)  # chamada da operação
        return v

    r = soma()                     # começa pela regra de menor prioridade
    if pos[0] != len(tokens):      # sobrou token: expressão inválida
        raise ValueError("Expressão inválida")
    return r

def calcular_local(op, a, b):
    # execução local das operações básicas (usada no servidor)
    if op == "add": return a + b
    if op == "sub": return a - b
    if op == "mul": return a * b
    if op == "div":
        if b == 0:
            raise ZeroDivisionError("Divisão por zero")  # trata divisão por zero
        return a / b
    raise ValueError("Operação desconhecida")

if __name__ == "__main__":
    # teste rápido: python parser.py
    print(avaliar("(10 + 15) * 4", calcular_local))   # esperado: 100.0
