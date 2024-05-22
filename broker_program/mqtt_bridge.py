import json
import time

import paho.mqtt.client as paho
from paho import mqtt

from config_interface import config_interface
from config import env_get, env_update
from buffer.buffer import Buffer
from mosq_funcs import *


connected = False
buffer = Buffer(env_get("BUFFER_PATH"), int(env_get("QUEUE_LIMIT")))


def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        print(f"Connected to {client._port}")
        if client._port == int(env_get("CLOUD_PORT")):
            connected = True
    else:
        print("Connection to MQTT broker failed. Retrying in 60 seconds...")
        time.sleep(60)
        client.reconnect()


def on_disconnect(client, userdata, rc, properties=None):
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


# TO-DO: broker update/delete
def cloud_on_message(client, userdata, msg):
    data_str = msg.payload.decode("utf-8")
    data = json.loads(data_str)
    levels = msg.topic.split("/")
    robot = levels[3]
    print(msg.topic, robot)
    if msg.topic.startswith(f"cloud/admin/{env_get('CLOUD_NAME')}/"):
        if data["command"] == "update":
            delete_mosquitto_user(robot)
            create_mosquitto_user(data["name"], data["password"])
        elif data["command"] == "delete":
            delete_mosquitto_user(robot)
    local_client.publish(msg.topic, payload=json.dumps(data), qos=1)
    print(f"Published message")


def local_on_message(client, userdata, msg):
    data_str = msg.payload.decode("utf-8")
    data = json.loads(data_str)
    if msg.topic == f"local/admin/{env_get('CLOUD_NAME')}/user":
        create_mosquitto_user(data["username"], data["password"])
    elif msg.topic.startswith("cloud/reg/"):
        if connected and buffer.queue_empty() and buffer.file_empty():
            cloud_client.publish(msg.topic, payload=json.dumps(data), qos=1)
            print(f"Published message")
        else:
            buffer.buffer_to_queue(msg.topic, data)


try:
    skipped, data = config_interface()
    if not skipped:
        env_update({"CLOUD_NAME": data["name"], "CLOUD_PASSWORD": data["password"]})

    cloud_client = paho.Client(
        client_id=env_get("CLOUD_NAME"), userdata=None, protocol=paho.MQTTv5
    )
    local_client = paho.Client(client_id=env_get("LOCAL_NAME"), userdata=None)
    cloud_client.on_connect = on_connect
    local_client.on_connect = on_connect
    local_client.on_message = local_on_message
    cloud_client.on_message = cloud_on_message
    cloud_client.on_disconnect = on_disconnect
    cloud_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

    cloud_client.username_pw_set(env_get("CLOUD_NAME"), env_get("CLOUD_PASSWORD"))
    local_client.username_pw_set(env_get("LOCAL_NAME"), env_get("LOCAL_PASSWORD"))

    cloud_client.connect(env_get("CLOUD_ADDRESS"), int(env_get("CLOUD_PORT")))
    local_client.connect(env_get("LOCAL_ADDRESS"), int(env_get("LOCAL_PORT")))

    local_client.loop_start()
    cloud_client.loop_start()

    local_client.subscribe(f"cloud/reg/{env_get('CLOUD_NAME')}/+/sensor-data", qos=1)
    local_client.subscribe(f"cloud/reg/{env_get('CLOUD_NAME')}/+/gps", qos=1)
    local_client.subscribe(f"local/admin/{env_get('CLOUD_NAME')}/user", qos=1)
    cloud_client.subscribe(f"cloud/admin/{env_get('CLOUD_NAME')}/+/dev", qos=1)
    cloud_client.subscribe(f"cloud/admin/{env_get('CLOUD_NAME')}/+/mission", qos=1)
    cloud_client.subscribe(f"cloud/reg/{env_get('CLOUD_NAME')}/+/control", qos=1)

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

# TO-DO: connectivity
