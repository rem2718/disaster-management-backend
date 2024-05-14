import json

import paho.mqtt.client as paho
from paho import mqtt


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to {client._port}")
    else:
        print(rc)


def on_disconnect(client, userdata, rc, properties=None):
    print("Disconnected from MQTT broker. Retrying in 60 seconds...")


def on_message(client, userdata, msg):
    data_str = msg.payload.decode("utf-8")
    data = json.loads(data_str)
    print(msg.topic, data)


cloud_client = paho.Client(client_id="cloud-test", userdata=None, protocol=paho.MQTTv5)
cloud_client.on_connect = on_connect
cloud_client.on_message = on_message
cloud_client.on_disconnect = on_disconnect
cloud_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
cloud_client.username_pw_set("cloud-test", "Cloud-Test12")
print(cloud_client.connect("27c434d04ed54e43a4c65102e26353b8.s1.eu.hivemq.cloud", 8883))

cloud_client.subscribe("#", qos=1)
topic = "cloud/reg/test-broker/test-ugv/control"
data = {"device": "motor", "command": "move", "value": [-1, 1]}
cloud_client.publish(topic, payload=json.dumps(data), qos=1)

cloud_client.disconnect()
