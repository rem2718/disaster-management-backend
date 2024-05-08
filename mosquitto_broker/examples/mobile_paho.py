import time
import paho.mqtt.client as paho
from paho import mqtt

user = 'test-mobile-app'
password = 'Test-mobile12'
address = '27c434d04ed54e43a4c65102e26353b8.s1.eu.hivemq.cloud'
port = 8883

# user = "test-broker"
# password = "test"
# address = "192.168.68.126"
# port = 1883
topic = "test-ugv/#"


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print(f'topic: {msg.topic}\nmessage: {str(msg.payload)}')


client = paho.Client(client_id=user, userdata=None, protocol=paho.MQTTv5)
# client = paho.Client(client_id=user, userdata=None)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(user, password)

client.connect(address, port)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe(topic, qos=1)

client.loop_forever()
