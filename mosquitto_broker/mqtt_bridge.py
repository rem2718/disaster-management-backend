import json
import time
import os

import paho.mqtt.client as paho
from dotenv import load_dotenv
from paho import mqtt

from buffer import Buffer

load_dotenv(".bridge_env")


cloud_user = os.getenv("CLOUD_USER")
cloud_password = os.getenv("CLOUD_PASS")
cloud_address = os.getenv("CLOUD_ADDRESS")
cloud_port = int(os.getenv("CLOUD_PORT"))

local_user = os.getenv("LOCAL_USER")
local_password = os.getenv("LOCAL_PASS")
local_address = os.getenv("LOCAL_ADDRESS")
local_port = int(os.getenv("LOCAL_PORT"))

buffer_path = os.getenv("BUFFER_PATH")
queue_limit = int(os.getenv("QUEUE_LIMIT"))

connected = False

buffer = Buffer(buffer_path, queue_limit)


def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        print(f"Connected to {client._port}")
        if client._port == local_port:
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


cloud_client = paho.Client(client_id=cloud_user, userdata=None, protocol=paho.MQTTv5)
local_client = paho.Client(client_id=local_user, userdata=None)

cloud_client.on_connect = on_connect
local_client.on_connect = on_connect
local_client.on_message = on_message
cloud_client.on_disconnect = on_disconnect

cloud_client.username_pw_set(cloud_user, cloud_password)
local_client.username_pw_set(local_user, local_password)
cloud_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

cloud_client.connect(cloud_address, cloud_port)
local_client.connect(local_address, local_port)

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
