import json
import time

import paho.mqtt.client as paho
from paho import mqtt


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to {client._port}")
    else:
        print(rc)


def on_disconnect(client, userdata, rc, properties=None):
    print("Disconnected from MQTT broker")


def on_message(client, userdata, msg):
    data_str = msg.payload.decode("utf-8")
    data = json.loads(data_str)
    print(msg.topic, data)


cloud_client = paho.Client(client_id="admin-broker", userdata=None)
cloud_client.on_connect = on_connect
cloud_client.on_message = on_message
cloud_client.on_disconnect = on_disconnect
cloud_client.username_pw_set("admin-broker", "BroAdmin@1984")

cloud_client.connect("192.168.68.125", 1883)
cloud_client.loop_start()

topic = "cloud/reg/test-broker/test-ugv/sensor-data"
cloud_client.subscribe(topic, qos=1)
while True:
    pass
