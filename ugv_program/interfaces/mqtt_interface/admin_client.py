import json

import paho.mqtt.client as paho

from config import config

admin_user = config.get("BROKER_ADMIN_NAME")
admin_password = config.get("BROKER_ADMIN_PASS")

PORT = 1883
CREATE_TOPIC = f"local/admin/{config.get('BROKER_NAME')}/user"


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


admin_client = paho.Client(client_id=admin_user, clean_session=False)
admin_client.username_pw_set(admin_user, admin_password)

admin_client.on_connect = on_connect
admin_client.on_message = on_message


def create_mqtt_user(addr, username, password):
    try:
        admin_client.connect(addr, PORT, keepalive=60 * 30)
        data = {"username": username, "password": password}
        admin_client.publish(CREATE_TOPIC, payload=json.dumps(data), qos=1)
        admin_client.disconnect()
        print("MQTT creds are created.")

    except KeyboardInterrupt:
        admin_client.disconnect()
