import json
import time

import paho.mqtt.client as paho

from config import Config

admin_user = Config.BROKER_ADMIN_NAME
admin_password = Config.BROKER_ADMIN_PASS

PORT = 1883


class RobotMQTTClient:
    def __init__(self, name, password, ip_addr):
        self.client = paho.Client(client_id=name, clean_session=False)
        self.client.username_pw_set(name, password)

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print(f"Connected to {client._port}")
                client.subscribe(f"cloud/reg/{name}/#", qos=1)
                # TO-DO: sub to local topic if you have any
            else:
                print("Connection to MQTT broker failed. Retrying in 60 seconds...")
                time.sleep(60)
                client.reconnect()

        def on_disconnect(client, userdata, rc, properties=None):
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
            print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message

        self.client.connect(ip_addr, PORT, keepalive=60 * 30)
        self.client.loop_start()

    def publish(self, topic, data):
        try:
            self.client.publish(topic, payload=json.dumps(data), qos=1)
        except:
            print("Unable to publish, try again")
            # TO-DO: here you can apply buffering mechanisms
