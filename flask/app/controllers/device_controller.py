from bson import ObjectId

from mongoengine.queryset.visitor import Q
from flask import jsonify

from app.utils.enums import DeviceStatus, DeviceType, MissionStatus
from app.models.mission_model import Mission
from app.models.device_model import Device
from app.utils.validators import *
from app.utils.extensions import *

MIN_LENGTH = 3
MAX_LENGTH = 20


@authorize_admin
@handle_exceptions
def register(user_type, name, password, mac, type, broker_id):
    null_validator(["Name", "Password", "Mac", "Type"], [name, password, mac, type])
    minlength_validator("Name", name, MIN_LENGTH)
    maxlength_validator("Name", name, MAX_LENGTH)
    mac_validator(mac)
    enum_validator("device", type, DeviceType)
    password_validator(password)
    existing_device = Device.objects(
        (Q(mac=mac) | Q(name=name)) & (Q(status__ne=DeviceStatus.INACTIVE))
    ).first()
    if existing_device:
        return err_res(409, "A device with the same MAC address is already registered.")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    if broker_id:
        broker_validator(broker_id)
        device = Device(
            name=name,
            password=hashed_password,
            mac=mac,
            type=type,
            broker_id=ObjectId(broker_id),
        )
    else:
        device = Device(name=name, password=hashed_password, mac=mac, type=type)

    if type == DeviceType.BROKER:
        mqtt_client.create_mqtt_user(device.name, password)

    device.save()
    data = {
        "message": "Device is registered successfully.",
        "device_id": str(device.id),
    }
    return jsonify(data), 201


@handle_exceptions
def rtmp_auth(name, password):
    null_validator(["Name", "Password"], [name, password])

    device = Device.objects(Q(name=name) & Q(status__ne=DeviceStatus.INACTIVE)).first()

    if not device or not device.check_password(password):
        return err_res(401, "Invalid device name or password.")

    data = {
        "message": f"Device {device.name} loggedin successfully.",
    }
    return jsonify(data), 200


@handle_exceptions
def get_info(device_id):
    null_validator(["Device ID"], [device_id])
    device = Device.objects.get(id=ObjectId(device_id))

    data = {
        "device_id": str(device.id),
        "name": device.name,
        "mac": device.mac,
        "type": device.type,
        "status": device.status,
    }
    if device.type != DeviceType.BROKER:
        broker_name = Device.objects.get(id=device.broker_id.id).name
        data["broker"] = {
            "broker_id": str(device.broker_id.id),
            "broker_name": broker_name,
        }

    if device.status == DeviceStatus.ASSIGNED:
        if device.type == DeviceType.BROKER:
            mission = Mission.objects(
                Q(broker_id=ObjectId(device_id))
                & Q(status__ne=MissionStatus.CANCELED)
                & Q(status__ne=MissionStatus.FINISHED)
            ).first()
        else:
            mission = Mission.objects(
                Q(device_ids=ObjectId(device_id))
                & Q(status__ne=MissionStatus.CANCELED)
                & Q(status__ne=MissionStatus.FINISHED)
            ).first()
        data["cur_mission"] = {
            "mission_id": str(mission.id),
            "name": mission.name,
            "status": mission.status,
        }

    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def get_all(
    user_type, page_number, page_size, name, statuses, types, broker_id, mission_id
):
    query, items = {}, []

    if name:
        query["name__icontains"] = name

    if statuses:
        query["status__in"] = statuses
    if types:
        query["type__in"] = types

    if broker_id:
        query["broker_id"] = ObjectId(broker_id)

    devices = Device.objects(**query).paginate(page=page_number, per_page=page_size)

    if mission_id:
        mission_devs = []
        mission = Mission.objects.get(id=mission_id)
        if DeviceType.BROKER in types:
            broker = Device.objects.get(id=mission.broker_id.id)
            items.append(
                {
                    "id": str(broker.id),
                    "name": broker.name,
                    "type": broker.type,
                    "status": broker.status,
                    "in_mission": True,
                }
            )
            mission_devs.append(str(broker.id))
        for dev in mission.device_ids:
            mission_devs.append(str(dev.id))
            device = Device.objects.get(id=str(dev.id))
            if types and device.type not in types:
                continue
            items.append(
                {
                    "id": str(device.id),
                    "name": device.name,
                    "type": device.type,
                    "status": device.status,
                    "in_mission": True,
                }
            )
        items += [
            {
                "id": str(device.id),
                "name": device.name,
                "type": device.type,
                "status": device.status,
                "in_mission": False,
            }
            for device in devices.items
            if str(device.id) not in mission_devs
        ]
    else:
        items = [
            {
                "id": str(device.id),
                "name": device.name,
                "type": device.type,
                "status": device.status,
            }
            for device in devices.items
        ]

    data = {
        "items": items,
        "has_next": devices.has_next,
        "has_prev": devices.has_prev,
        "page": devices.page,
        "total_pages": devices.pages,
    }

    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def get_count(user_type, statuses, types):
    query = {}

    if statuses:
        query["status__in"] = statuses
    if types:
        query["type__in"] = types

    device_count = Device.objects(**query).count()

    data = {"status": statuses, "type": types, "count": device_count}

    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def get_broker_id(user_type, mac):
    null_validator(["MAC Address"], [mac])
    mac_validator(mac)
    broker = Device.objects(Q(mac=mac) & Q(status__ne=DeviceStatus.INACTIVE)).first()

    if broker and broker.type == DeviceType.BROKER:
        data = {"broker_id": str(broker.id), "broker_name": broker.name}
        return jsonify(data), 200

    return err_res(404, "Broker not found")


@authorize_admin
@handle_exceptions
def update(user_type, device_id, name, old_password, new_password):
    device = Device.objects.get(id=device_id)
    null_validator(["Password"], [old_password])

    dev_name = device.name
    dev_password = old_password

    if not device.check_password(old_password):
        return err_res(401, "Incorrect old password try again.")

    if name:
        if device.name != name:
            existing_device = Device.objects(name=name).first()
            if existing_device:
                return err_res(409, "Name is already taken.")
        else:
            return err_res(409, "The name provided is identical to the current one.")
        minlength_validator("Name", name, MIN_LENGTH)
        maxlength_validator("Name", name, MAX_LENGTH)
        device.name = name

    if new_password:
        if old_password == new_password:
            return err_res(409, "The new password is identical to the current one.")
        password_validator(new_password)
        device.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        dev_password = new_password

    if device.type == DeviceType.BROKER:
        mqtt_data = {"command": "update", "name": device.name, "password": dev_password}
        mqtt_client.publish_broker(dev_name, mqtt_data)
        mqtt_client.delete_mqtt_user(dev_name)
        mqtt_client.create_mqtt_user(device.name, dev_password)
    else:
        broker_name = Device.objects.get(id=device.broker_id.id).name
        mqtt_data = {"command": "update", "name": device.name, "password": dev_password}
        mqtt_client.publish_dev(broker_name, dev_name, mqtt_data)

    device.save()
    data = {
        "message": "Device information is updated successfully.",
        "name": device.name,
    }
    return jsonify(data), 200


@handle_exceptions
def update_state(device_id, state):
    device = Device.objects.get(id=device_id)
    null_validator(["State"], [state])
    if state not in ["control", "auto"]:
        return err_res(400, "Invalid state.")

    if device.type not in [DeviceType.UGV]:
        return err_res(409, "You can't change the state of this device.")

    broker_name = Device.objects.get(id=device.broker_id.id).name
    mqtt_data = {"command": "switch", "state": state}
    mqtt_client.publish_dev(broker_name, device.name, mqtt_data)
    data = {
        "message": "Device state is updated successfully.",
    }
    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def update_broker(user_type, name, broker_mac):
    device = Device.objects(Q(name=name) & Q(status__ne=DeviceStatus.INACTIVE)).first()
    broker = Device.objects(
        Q(mac=broker_mac) & Q(status__ne=DeviceStatus.INACTIVE)
    ).first()

    if not device:
        return err_res(404, "Device not found.")

    if not broker:
        err_res(404, "Broker not found.")

    device.broker_id = broker.id

    device.save()
    data = {
        "message": "Device broker is updated successfully.",
        "broker_name": broker.name,
    }
    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def deactivate(user_type, device_id):
    null_validator(["Device ID"], [device_id])
    device = Device.objects.get(id=device_id)
    if device.status == DeviceStatus.INACTIVE:
        return err_res(409, "Device is already Inactive.")

    missions = Mission.objects(
        device_ids__in=[ObjectId(device_id)],
        status__in=[MissionStatus.CREATED, MissionStatus.ONGOING, MissionStatus.PAUSED],
    )
    for mission in missions:
        mission.update(pull__device_ids=ObjectId(device_id))

    if device.type == DeviceType.BROKER:
        if device.status == DeviceStatus.ASSIGNED:
            return err_res(409, "Assigned brokers can't be deleted.")
        mqtt_data = {"command": "delete", "name": device.name}
        mqtt_client.publish_broker(device.name, mqtt_data)
        mqtt_client.delete_mqtt_user(device.name)
        Device.objects(broker_id=ObjectId(device_id)).update(set__broker_id=None)
    else:
        if device.broker_id: 
            broker_name = Device.objects.get(id=device.broker_id.id).name
            mqtt_data = {"command": "delete", "name": device.name}
            mqtt_client.publish_dev(broker_name, device.name, mqtt_data)

    Device.objects(id=device_id).update(set__status=DeviceStatus.INACTIVE)
    return jsonify({"message": "Device is deactivated successfully."}), 200
