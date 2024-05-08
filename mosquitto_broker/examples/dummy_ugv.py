# pip install paho-mqtt==1.6.1
from datetime import datetime
import random
import time
import json

import paho.mqtt.client as paho
from paho import mqtt

user = "test-broker"
password = "Test-broker12"
address = "df29475dfed14680a1a57a1c8e98b400.s2.eu.hivemq.cloud"
port = 8883

topic = "cloud/test-ugv/sensor_data"
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


client = paho.Client(client_id=user, userdata=None, protocol=paho.MQTTv5)
client.username_pw_set(user, password)

client.on_connect = on_connect
client.on_message = on_message
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

client.connect(address, port)
client.loop_start()

try:
    while True:
        data = read_sensors()
        client.publish(topic, payload=json.dumps(data), qos=1)
        print(f"Published message: {data['id']}")
        time.sleep(30)

except KeyboardInterrupt:
    print("Disconnecting from the MQTT broker...")
    client.disconnect()
    client.loop_stop()
