import paho.mqtt.client as mqtt   # biblioteca cliente MQTT

def on_connect(client, userdata, flags, rc, props):
    client.subscribe("caldeira/alertas/#")       # escuta todos os alertas
    print("Alarms aguardando alertas...")

def on_message(client, userdata, msg):
    # exibe o alarme recebido de forma destacada
    print(f"*** ALARME [{msg.topic}] {msg.payload.decode()} ***")

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # cria o cliente
c.on_connect = on_connect         # callback de conexão
c.on_message = on_message         # callback de mensagem
c.connect("localhost", 1883)      # conecta ao broker
c.loop_forever()                  # fica escutando para sempre