import json
import time

import paho.mqtt.client as paho

PORT = 1883


class MQTTClient:

    def __init__(self, name, password, ip_addr):
        self.name = name
        self.password = password
        self.ip_addr = ip_addr
        self.client = paho.Client(client_id=name, clean_session=False)

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print(f"Connected to {client._port}")
            else:
                print("Connection to MQTT broker failed. Retrying in 60 seconds...")
                time.sleep(60)
                client.reconnect()

        self.client.on_connect = on_connect
        self.client.username_pw_set(name, password)

    def create_mqtt_user(self, username, password):
        try:
            topic = "cloud/admin/user"
            data = {"command": "create", "name": username, "password": password}
            self.client.connect(self.ip_addr, PORT)
            self.client.publish(topic, payload=json.dumps(data), qos=1)
            self.client.disconnect()
        except Exception as e:
            print("Unable to publish, try again", str(e))

    def delete_mqtt_user(self, username):
        try:
            topic = "cloud/admin/user"
            data = {"command": "delete", "name": username}
            self.client.connect(self.ip_addr, PORT)
            self.client.publish(topic, payload=json.dumps(data), qos=1)
            self.client.disconnect()
        except:
            print("Unable to publish, try again")

    def publish_mission(self, broker_name, command, dev_name=None):
        try:
            if dev_name:
                topic = f"cloud/admin/{broker_name}/{dev_name}/mission"
            else:
                topic = f"cloud/admin/{broker_name}/all/mission"
            data = {"command": command}
            self.client.connect(self.ip_addr, PORT)
            self.client.publish(topic, payload=json.dumps(data), qos=1)
            self.client.disconnect()
        except Exception as e:
            print("Unable to publish, try again", e)

    def publish_dev(self, broker_name, dev_name, data):
        try:
            topic = f"cloud/admin/{broker_name}/{dev_name}/dev"
            self.client.connect(self.ip_addr, PORT)
            self.client.publish(topic, payload=json.dumps(data), qos=1)
            self.client.disconnect()
        except:
            print("Unable to publish, try again")

    def publish_broker(self, broker_name, data):
        try:
            topic = f"cloud/admin/{broker_name}/dev"
            self.client.connect(self.ip_addr, PORT)
            self.client.publish(topic, payload=json.dumps(data), qos=1)
            self.client.disconnect()
        except:
            print("Unable to publish, try again")
