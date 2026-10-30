import paho.mqtt.client as mqtt   # biblioteca cliente MQTT
import time                       # para timestamps e esperas
import sys                        # para ler argumentos
from collections import deque     # fila para guardar as leituras

BROKER = "localhost"              # endereço do broker
PORTA = 1883                      # porta do MQTT
PERIODO = int(sys.argv[1]) if len(sys.argv) > 1 else 60   # período do cálculo (s)
JANELA = 120                      # janela da média: últimos 120 segundos

leituras = deque()                # guarda tuplas (timestamp, temperatura)
media_anterior = None             # média anterior, para comparar

def on_connect(client, userdata, flags, rc, props):
    client.subscribe("caldeira/temperatura/+")   # escuta todos os sensores
    print("CAT conectado e inscrito em caldeira/temperatura/+")

def on_message(client, userdata, msg):
    temp = float(msg.payload.decode())           # converte o payload em número
    leituras.append((time.time(), temp))         # guarda a leitura com a hora
    print(f"[CAT] recebeu {temp} de {msg.topic}")

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # cria o cliente
c.on_connect = on_connect         # callback de conexão
c.on_message = on_message         # callback de mensagem
c.connect(BROKER, PORTA)          # conecta ao broker
c.loop_start()                    # rede em segundo plano

while True:                       # laço principal do cálculo
    time.sleep(PERIODO)           # espera o período
    agora = time.time()           # hora atual
    while leituras and agora - leituras[0][0] > JANELA:
        leituras.popleft()        # descarta leituras com mais de 120s
    if not leituras:              # sem dados na janela
        print("[CAT] sem leituras na janela")
        continue
    media = sum(t for _, t in leituras) / len(leituras)   # calcula a média
    print(f"[CAT] média dos últimos {JANELA}s = {media:.2f}")
    if media_anterior is not None and abs(media - media_anterior) >= 5:
        c.publish("caldeira/alertas/aumento-repentino",
                  f"Aumento repentino: {media_anterior:.1f} -> {media:.1f}")
    if media > 200:               # média acima de 200 graus
        c.publish("caldeira/alertas/temperatura-alta",
                  f"Temperatura alta: média {media:.1f}")
    media_anterior = media        # atualiza a média anterior
