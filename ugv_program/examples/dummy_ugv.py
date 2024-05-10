# pip install paho-mqtt==1.6.1
from datetime import datetime
import random
import time
import json

import paho.mqtt.client as paho
from paho import mqtt

user = "test-ugv"
password = "test"

address = "192.168.68.121"
port = 1883

topic = "local/reg/sensor-data"
count = 0


def read_sensors():
    global count
    temperature = random.uniform(20, 50)
    humidity = random.uniform(0, 100)
    distance = random.uniform(10, 500)
    light = random.uniform(10, 1000)
    timestamp = datetime.now().isoformat()
    data = {
        "id": count,
        "humidity": humidity,
        "temperature": temperature,
        "distance": distance,
        "light": light,
        "timestamp": timestamp,
    }
    count += 1
    return data


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


client = paho.Client(client_id=user)
client.username_pw_set(user, password)

client.on_connect = on_connect
client.on_message = on_message

client.connect(address, port)
client.loop_start()

try:
    while True:
        data = read_sensors()
        client.publish(topic, payload=json.dumps(data), qos=1)
        print(f"Published message: {data['id']}")
        print("done")
        time.sleep(30)

except KeyboardInterrupt:
    print("Disconnecting from the MQTT broker...")
    client.disconnect()
    client.loop_stop()
