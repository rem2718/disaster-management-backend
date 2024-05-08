import json
import time

import paho.mqtt.client as paho
from paho import mqtt

from buffer.buffer import Buffer
from config import Config
from mqtt_funcs import *


connected = False
buffer = Buffer(Config.BUFFER_PATH, Config.QUEUE_LIMIT)


def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        print(f"Connected to {client._port}")
        if client._port == Config.LOCAL_PORT:
            client.subscribe("cloud/#", qos=1)
        else:
            connected = True
    else:
        print("Connection to MQTT broker failed. Retrying in 60 seconds...")
        time.sleep(60)
        client.reconnect()


def on_disconnect(client, userdata, rc):
    global connected
    connected = False
    print("Disconnected from MQTT broker. Retrying in 60 seconds...")
    while True:
        try:
            rc = client.reconnect()
            if rc == 0:
                break
            else:
                time.sleep(60)
        except Exception as e:
            time.sleep(60)


def on_message(client, userdata, msg):
    if msg.topic.startswith("cloud"):
        topic = msg.topic[6:]
        data_str = msg.payload.decode("utf-8")
        data = json.loads(data_str)
        if connected and buffer.queue_empty() and buffer.file_empty():
            cloud_client.publish(topic, payload=json.dumps(data), qos=1)
            print(f"Published message: {data['id']}")
        else:
            buffer.buffer_to_queue(topic, data)

    elif msg.topic == "local/admin/create_user":
        data_str = msg.payload.decode("utf-8")
        data = json.loads(data_str)
        create_mosquitto_user(data["username"], data["password"])

    elif msg.topic == "local/admin/delete_user":
        data_str = msg.payload.decode("utf-8")
        data = json.loads(data_str)
        create_mosquitto_user(data["username"])


cloud_client = paho.Client(
    client_id=Config.CLOUD_USER, userdata=None, protocol=paho.MQTTv5
)
local_client = paho.Client(client_id=Config.LOCAL_USER, userdata=None)

cloud_client.on_connect = on_connect
local_client.on_connect = on_connect
local_client.on_message = on_message
cloud_client.on_disconnect = on_disconnect

cloud_client.username_pw_set(Config.CLOUD_USER, Config.CLOUD_PASS)
local_client.username_pw_set(Config.LOCAL_USER, Config.LOCAL_PASS)
cloud_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

cloud_client.connect(Config.CLOUD_ADDRESS, Config.CLOUD_PORT)
local_client.connect(Config.LOCAL_ADDRESS, Config.LOCAL_PORT)

local_client.loop_start()
cloud_client.loop_start()

try:
    while True:
        if connected:
            if not buffer.file_empty():
                buffer.publish_file(cloud_client)
            if not buffer.queue_empty():
                buffer.publish_queue(cloud_client)

except KeyboardInterrupt:
    print("Bridge Program terminated...")
    local_client.disconnect()
    local_client.loop_stop()
    cloud_client.disconnect()
    cloud_client.loop_stop()
