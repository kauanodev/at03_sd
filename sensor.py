import paho.mqtt.client as mqtt   # biblioteca cliente MQTT
import random                     # gera valores aleatórios de temperatura
import time                       # permite esperar entre as leituras
import sys                        # permite ler argumentos da linha de comando

BROKER = "localhost"              # endereço do broker MQTT
PORTA = 1883                      # porta padrão do MQTT
ID = sys.argv[1] if len(sys.argv) > 1 else "1"                  # id do sensor
INTERVALO = int(sys.argv[2]) if len(sys.argv) > 2 else 60       # segundos entre leituras
BASE = float(sys.argv[3]) if len(sys.argv) > 3 else 100.0       # temperatura base

TOPICO = f"caldeira/temperatura/{ID}"   # cada sensor publica no seu tópico

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # cria o cliente MQTT
c.connect(BROKER, PORTA)          # conecta ao broker
c.loop_start()                    # processa a rede em segundo plano

print(f"Sensor {ID} publicando em {TOPICO} a cada {INTERVALO}s")
while True:                       # repete para sempre
    temp = round(BASE + random.uniform(-2, 2), 2)   # temperatura simulada
    c.publish(TOPICO, str(temp))  # publica no tópico
    print(f"[Sensor {ID}] enviou {temp}")           # mostra no console
    time.sleep(INTERVALO)         # espera até a próxima leitura
