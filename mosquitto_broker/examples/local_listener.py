import paho.mqtt.client as paho
import time

user = "test-broker"
password = "test"
address = "192.168.68.124"
port = 1883


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to {client._port}")
        client.subscribe("#", qos=1)
    else:
        print("Connection to MQTT broker failed. Retrying in 60 seconds...")
        time.sleep(60)
        client.reconnect()


def on_disconnect(client, userdata, rc):
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


client = paho.Client(client_id=user, userdata=None, clean_session=False)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.username_pw_set(user, password)

client.connect(address, port)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Disconnecting from the MQTT broker...")
    client.disconnect()
    client.loop_stop()
