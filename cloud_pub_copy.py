import json
import time

import paho.mqtt.client as paho
from paho import mqtt

import random

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

cloud_client = paho.Client(client_id="test-ugv", userdata=None)
cloud_client.on_connect = on_connect
cloud_client.on_message = on_message
cloud_client.on_disconnect = on_disconnect

# cloud_client.username_pw_set("test-broker", "testBroker@1984")
cloud_client.username_pw_set("admin-web", "AdmWeb@1984")

cloud_client.loop_start()
cloud_client.connect("51.79.158.202", 1883)

topic = "cloud/admin/user"
# topic = "cloud/admin/test-broker/all/mission"
# topic1 = "cloud/reg/test-broker/test-dev/gps"
# topic2 = "cloud/reg/test-broker/test-dev/sensor-data"


data = {"command": "create", "name": "user123", "password": "New_password123"}
# data = {"command": "start"} 
cloud_client.publish(topic, payload=json.dumps(data), qos=1)
time.sleep(5)

# data = {"device": "motor", "command": "move", "value": [-1, 1]}

# data = {"command":"switch", "state":"control"}
# data = {"username": "test-a", "password": "test"}

cloud_client.disconnect()
cloud_client.loop_stop()

