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


# cloud_client = paho.Client(client_id="cloud-test", userdata=None, protocol=paho.MQTTv5)
cloud_client = paho.Client(client_id="test-ugv", userdata=None)
cloud_client.on_connect = on_connect
cloud_client.on_message = on_message
cloud_client.on_disconnect = on_disconnect

cloud_client.username_pw_set("test-broker", "testBroker@1984")
# cloud_client.username_pw_set("user2", "New_password123#")
# cloud_client.username_pw_set("admin-web", "AdmWeb@1984")

cloud_client.loop_start()
# cloud_client.connect("192.168.68.125", 1883)
cloud_client.connect("51.79.158.202", 1883)

# topic = "cloud/admin/user"
# topic = "cloud/admin/test-broker/test-dev/dev"
topic1 = "cloud/reg/test-broker/test-dev/gps"
topic2 = "cloud/reg/test-broker/test-dev/sensor-data"

while True:
    lat = random.uniform(-90, 90)
    long = random.uniform(-180, 180)
    temp = random.uniform(-20, 50)
    humidity = random.uniform(0, 100)
    gas = random.uniform(100, 1000)
    co2 = random.uniform(10, 200)
    tvoc = random.uniform(10, 200)
    gyroscope1 = random.uniform(0, 360)
    gyroscope2 = random.uniform(0, 360)
    gyroscope3 = random.uniform(0, 360)
    accelerometer1 = random.uniform(0, 360)
    accelerometer2 = random.uniform(0, 360)
    accelerometer3 = random.uniform(0, 360)
    ir = random.uniform(1,10)
    ultrasonic = random.uniform(0, 100)
    sound = random.uniform(0, 1000)
    battery = random.uniform(0, 100)
    
    data = [
        {
            "sensor": "temperature",
            "value": temp,
            "unit": "°C"
        },
        {
            "sensor": "humidity",
            "value": humidity,
            "unit": "%"
        },
        {
            "sensor": "gas",
            "value": gas,
            "unit": "ppm"
        },
        {
            "sensor": "co2",
            "value": co2,
            "unit": "ppm"
        },
        {
            "sensor": "tvoc",
            "value": tvoc,
            "unit": "ppb"
        },
        {
            "sensor": "accelerometer",
            "value": [
                accelerometer1,
                accelerometer2,
                accelerometer3
            ],
            "unit": "m/s^2"
        },
        {
            "sensor": "gyroscope",
            "value": [
                gyroscope1,
                gyroscope2,
                gyroscope3
            ],
            "unit": "°/s"
        },
        {
            "sensor": "ir",
            "value": ir,
            "unit": ""
        },
        {
            "sensor": "ultrasonic",
            "value": ultrasonic,
            "unit": "cm"
        },
        {
            "sensor": "sound",
            "value": sound,
            "unit": ""
        },
        {
            "sensor": "battery",
            "value": battery,
            "unit": "%"
        }
    ]

    gps = {"lat": lat, "long": long}
    print(gps)
    cloud_client.publish(topic1, payload=json.dumps(gps), qos=1)
    cloud_client.publish(topic2, payload=json.dumps(data), qos=1)
    time.sleep(5)

# data = {"device": "motor", "command": "move", "value": [-1, 1]}

# data = {"command": "start", "name": "test-broker", "password": "Test-broker12"}
# data = {"command":"switch", "state":"control"}
# data = {"username": "test-a", "password": "test"}

cloud_client.disconnect()
cloud_client.loop_stop()

