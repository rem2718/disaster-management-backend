import json
import time
import sys

import paho.mqtt.client as paho

from config_interface import config_interface
from buffer.buffer import Buffer
from config import config
from mosq_funcs import *


connected = False
buffer = Buffer(config.get("BUFFER_PATH"), int(config.get("QUEUE_LIMIT")))


def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        print(f"Connected to {client._port}")
        if client._port == int(config.get("CLOUD_PORT")):
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


def cloud_on_message(client, userdata, msg):
    data_str = msg.payload.decode("utf-8")
    data = json.loads(data_str)
    levels = msg.topic.split("/")
    robot = levels[3]
    print(msg.topic, robot)
    local_client.publish(msg.topic, payload=json.dumps(data), qos=1)

    if msg.topic.startswith(f"cloud/admin/{config.get('CLOUD_NAME')}/dev"):
        if data["command"] == "update":
            config.update(
                {"CLOUD_NAME": data["name"], "CLOUD_PASSWORD": data["password"]}
            )
            cloud_client.username_pw_set(
                config.get("CLOUD_NAME"), config.get("CLOUD_PASSWORD")
            )
        elif data["command"] == "delete":
            config.update({"CLOUD_NAME": "", "CLOUD_PASSWORD": ""})
            print("Bridge Program terminated...")
            local_client.disconnect()
            local_client.loop_stop()
            cloud_client.disconnect()
            cloud_client.loop_stop()
            sys.exit()
    elif msg.topic.startswith(f"cloud/admin/{config.get('CLOUD_NAME')}/"):
        if data["command"] == "update":
            delete_mosquitto_user(robot)
            create_mosquitto_user(data["name"], data["password"])
        elif data["command"] == "delete":
            delete_mosquitto_user(robot)
    print(f"Published message")


def local_on_message(client, userdata, msg):
    data_str = msg.payload.decode("utf-8")
    data = json.loads(data_str)
    if msg.topic == f"local/admin/{config.get('CLOUD_NAME')}/user":
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
        config.update({"CLOUD_NAME": data["name"], "CLOUD_PASSWORD": data["password"]})

    cloud_client = paho.Client(
        client_id=config.get("CLOUD_NAME"), userdata=None, clean_session=False
    )
    local_client = paho.Client(
        client_id=config.get("LOCAL_NAME"), userdata=None, clean_session=False
    )
    cloud_client.on_connect = on_connect
    local_client.on_connect = on_connect
    local_client.on_message = local_on_message
    cloud_client.on_message = cloud_on_message
    cloud_client.on_disconnect = on_disconnect

    cloud_client.username_pw_set(config.get("CLOUD_NAME"), config.get("CLOUD_PASSWORD"))
    local_client.username_pw_set(config.get("LOCAL_NAME"), config.get("LOCAL_PASSWORD"))

    cloud_client.connect(
        config.get("CLOUD_ADDRESS"), int(config.get("CLOUD_PORT")), keepalive=60 * 30
    )
    local_client.connect(
        config.get("LOCAL_ADDRESS"), int(config.get("LOCAL_PORT")), keepalive=60 * 30
    )

    local_client.loop_start()
    cloud_client.loop_start()

    local_client.subscribe(f"cloud/reg/{config.get('CLOUD_NAME')}/+/sensor-data", qos=1)
    local_client.subscribe(f"cloud/reg/{config.get('CLOUD_NAME')}/+/gps", qos=1)
    local_client.subscribe(f"local/admin/{config.get('CLOUD_NAME')}/user", qos=1)
    cloud_client.subscribe(f"cloud/admin/{config.get('CLOUD_NAME')}/dev", qos=1)
    cloud_client.subscribe(f"cloud/admin/{config.get('CLOUD_NAME')}/+/dev", qos=1)
    cloud_client.subscribe(f"cloud/admin/{config.get('CLOUD_NAME')}/+/mission", qos=1)
    cloud_client.subscribe(f"cloud/reg/{config.get('CLOUD_NAME')}/+/control", qos=1)

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
