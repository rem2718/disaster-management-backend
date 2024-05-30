import json
import time

import paho.mqtt.client as paho


PORT = 1883


class RobotMQTTClient:
    def __init__(self, name, password, broker_name, ip_addr, motion_queue, admin_queue):
        self.name = name
        self.password = password
        self.ip_addr = ip_addr
        self.broker_name = broker_name
        self.client = paho.Client(client_id=name, clean_session=False)

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print(f"Connected to {client._port}")
                client.subscribe(f"cloud/reg/{broker_name}/{name}/control", qos=1)
                client.subscribe(f"cloud/admin/{broker_name}/{name}/dev", qos=1)
                client.subscribe(f"cloud/admin/{broker_name}/all/+", qos=1)
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
            topic = msg.topic
            data_str = msg.payload.decode("utf-8")
            data = json.loads(data_str)
            topics_levels = topic.split("/")
            command = topics_levels[-1]
            print(f"A message received for {command}")
            if command == "mission" or command == "dev" or command == "broker":
                admin_queue.append((command, data))
            elif command == "control":
                motion_queue.append((command, data))
            else:
                print("Invalid topic level")

        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.username_pw_set(name, password)
        self.client.connect(self.ip_addr, PORT, keepalive=60 * 30)
        self.client.loop_start()

    def publish(self, topic, data):
        try:
            self.client.publish(topic, payload=json.dumps(data), qos=1)
        except:
            print("Unable to publish, try again")
            # TO-DO: here you can apply buffering mechanisms

    def update_broker(self, broker_name):
        self.client.unsubscribe(f"cloud/reg/{self.broker_name}/{self.name}/control")
        self.client.unsubscribe(f"cloud/admin/{self.broker_name}/{self.name}/dev")
        self.client.unsubscribe(f"cloud/admin/{self.broker_name}/all/+")
        self.broker_name = broker_name
        self.client.subscribe(
            f"cloud/reg/{self.broker_name}/{self.name}/control", qos=1
        )
        self.client.subscribe(f"cloud/admin/{self.broker_name}/{self.name}/dev", qos=1)
        self.client.subscribe(f"cloud/admin/{self.broker_name}/all/+", qos=1)

    def stop_client(self):
        print("Disconnecting from MQTT broker")
        self.client.disconnect()
        # self.client.loop_stop()
