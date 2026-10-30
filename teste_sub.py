import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode())

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
c.on_message = on_message
c.connect("localhost", 1883)
c.subscribe("teste/#")
c.loop_forever()