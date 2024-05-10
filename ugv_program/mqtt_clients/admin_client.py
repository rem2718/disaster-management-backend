import json

import paho.mqtt.client as paho

from config import Config

admin_user = Config.BROKER_ADMIN_NAME
admin_password = Config.BROKER_ADMIN_PASS

PORT = 1883
CREATE_TOPIC = "local/admin/create-user"
DELETE_TOPIC = "local/admin/delete-user"


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


admin_client = paho.Client(client_id=admin_user)
admin_client.username_pw_set(admin_user, admin_password)

admin_client.on_connect = on_connect
admin_client.on_message = on_message


def create_mqtt_user(addr, username, password):
    try:
        admin_client.connect(addr, PORT)
        data = {"username": username, "password": password}
        admin_client.publish(CREATE_TOPIC, payload=json.dumps(data), qos=1)
        admin_client.disconnect()

    except KeyboardInterrupt:
        admin_client.disconnect()


def delete_mqtt_user(addr, username):
    try:
        admin_client.connect(addr, PORT)
        data = {"username": username}
        admin_client.publish(DELETE_TOPIC, payload=json.dumps(data), qos=1)
        admin_client.disconnect()

    except KeyboardInterrupt:
        admin_client.disconnect()
