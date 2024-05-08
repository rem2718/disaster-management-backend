from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties
import paho.mqtt.client as paho
from paho import mqtt
import time

cloud_user = "test-ugv"
cloud_password = "Test-ugv12"
cloud_address = "df29475dfed14680a1a57a1c8e98b400.s2.eu.hivemq.cloud"
cloud_port = 8883


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to {client._port}")
        client.subscribe("#", qos=1)
    else:
        print("Connection to MQTT broker failed. Retrying in 60 seconds...")
        time.sleep(60)
        client.reconnect()


def on_disconnect(client, userdata, flags, rc):
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
    print(f"topic: {msg.topic}\n message:{str(msg.payload)}")


cloud_client = paho.Client(client_id=cloud_user, userdata=None, protocol=paho.MQTTv5)
properties = Properties(PacketTypes.CONNECT)
properties.SessionExpiryInterval = 0xFFFFFFFF

cloud_client.on_connect = on_connect
cloud_client.on_message = on_message
cloud_client.on_disconnect = on_disconnect

cloud_client.username_pw_set(cloud_user, cloud_password)
cloud_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

cloud_client.connect(
    cloud_address, cloud_port, clean_start=False, properties=properties
)

try:
    cloud_client.loop_forever()
except KeyboardInterrupt:
    print("Disconnecting from the MQTT broker...")
    cloud_client.disconnect()
    cloud_client.loop_stop()
