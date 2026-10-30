
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
c.connect("localhost", 1883)
c.publish("teste/oi", "funcionou")
c.disconnect()