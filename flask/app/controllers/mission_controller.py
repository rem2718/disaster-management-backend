from datetime import datetime
from bson import ObjectId

from flask import jsonify

from app.utils.enums import MissionStatus, UserStatus, DeviceStatus
from app.models.user_model import User, cur_mission
from app.models.mission_model import Mission
from app.models.device_model import Device
from app.utils.validators import *
from app.utils.extensions import *


def update_cur_mission(mission, type):
    for usr in mission.user_ids:
        user = User.objects.get(id=str(usr.id))
        for cur_mission in user.cur_missions:
            if str(cur_mission._id) == str(mission.id):
                cur_mission[type] = mission[type]
                break
        user.save()


def update_lists(ids_list, case, mission=None):
    match case:
        case "add_user":
            cur_m = cur_mission(
                _id=mission.id, name=mission.name, status=mission.status
            )
            User.objects(id__in=ids_list).update(
                push__cur_missions=cur_m, set__status=UserStatus.ASSIGNED
            )

        case "delete_user":
            for _id in ids_list:
                user = User.objects.get(id=_id)
                if len(user.cur_missions) == 1:
                    user.update(set__cur_missions=[], status=UserStatus.AVAILABLE)
                else:
                    user.cur_missions = [
                        cur_m
                        for cur_m in user.cur_missions
                        if cur_m["_id"] != mission.id
                    ]
                    user.save()

        case "add_device":
            Device.objects(id__in=ids_list).update(set__status=DeviceStatus.ASSIGNED)

        case "delete_device":
            Device.objects(id__in=ids_list).update(set__status=DeviceStatus.AVAILABLE)


def split_sets(existing_list, provided_list):
    existing_set = set(str(e.id) for e in existing_list)
    provided_set = set(provided_list)
    added_ids = provided_set - existing_set
    deleted_ids = existing_set - provided_set
    return added_ids, deleted_ids


@authorize_admin
@handle_exceptions
def create(user_type, name, device_ids, user_ids):
    null_validator(["name", "device_ids", "user_ids"], [name, device_ids, user_ids])
    existing_mission = Mission.objects(name=name).first()
    if existing_mission:
        return err_res(409, "Mission name is already taken.")
    minlength_validator("Name", name, 3)
    maxlength_validator("Name", name, 20)
    device_validator(device_ids)
    user_validator(user_ids)

    mission = Mission(name=name, device_ids=device_ids, user_ids=user_ids)
    mission.save()
    update_lists(user_ids, "add_user", mission)
    update_lists(device_ids, "add_device")
    data = {
        "message": "Mission is created successfully.",
        "mission_id": str(mission.id),
    }
    return jsonify(data), 201


@handle_exceptions
def get_info(user_type, mission_id):
    mission = Mission.objects.get(id=mission_id)
    devices = []
    for d in mission.device_ids:
        device = Device.objects.get(id=str(d.id))
        devices.append(
            {"id": str(device.id), "name": device.name, "type": device.type.value}
        )

    data = {
        "id": str(mission.id),
        "name": mission.name,
        "start_date": mission.start_date,
        "end_date": mission.end_date,
        "status": mission.status.value,
        "devices": devices,
    }

    if user_type == UserType.ADMIN.value:
        users = []
        for r in mission.user_ids:
            user = User.objects.get(id=str(r.id))
            users.append({"id": str(user.id), "username": user.username})
        data["users"] = users

    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def get_all(user_type, page_number, page_size, name, statuses):
    offset = (page_number - 1) * page_size
    query = {}

    if name:
        query["name__icontains"] = name
    if statuses:
        query["status__in"] = statuses

    missions = Mission.objects(**query).skip(offset).limit(page_size)
    data = [
        {"id": str(mission.id), "name": mission.name, "status": mission.status.value}
        for mission in missions
    ]
    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def get_count(user_type, statuses):
    query = {}

    if statuses:
        query["status__in"] = statuses

    mission_count = Mission.objects(**query).count()

    data = {"status": statuses, "count": mission_count}

    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def update(user_type, mission_id, name, device_ids, user_ids):
    mission = Mission.objects.get(id=mission_id)
    if mission.status in [MissionStatus.CANCELED, MissionStatus.FINISHED]:
        return err_res(
            409, "You can't update the mission information after it's finished."
        )

    if name and name != mission.name:
        minlength_validator("Name", name, 3)
        maxlength_validator("Name", name, 20)
        mission.name = name
        update_cur_mission(mission, "name")

    if device_ids != None:
        added_ids, deleted_ids = split_sets(mission.device_ids, device_ids)
        device_validator(added_ids)
        update_lists(added_ids, "add_device")
        update_lists(deleted_ids, "delete_device")
        mission.device_ids = [ObjectId(_id) for _id in device_ids]

    if user_ids != None:
        user_validator(user_ids)
        added_ids, deleted_ids = split_sets(mission.user_ids, user_ids)
        update_lists(added_ids, "add_user", mission)
        update_lists(deleted_ids, "delete_user", mission)
        mission.user_ids = [ObjectId(_id) for _id in user_ids]

    mission.save()
    data = {
        "message": "mission is updated successfully.",
        "id": str(mission.id),
        "name": mission.name,
        "status": mission.status.value,
        "user_ids": [str(user.id) for user in mission.user_ids],
        "device_ids": [str(device.id) for device in mission.device_ids],
    }
    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def change_status(user_type, mission_id, command):
    mission = Mission.objects.get(id=mission_id)
    ongoing_statues = [MissionStatus.ONGOING, MissionStatus.PAUSED]
    finished_statues = [MissionStatus.CANCELED, MissionStatus.FINISHED]
    if mission.status in finished_statues:
        return err_res(409, "This mission is already finished.")

    match command:
        case "start":
            if mission.status in ongoing_statues:
                return err_res(409, "This mission is already started.")
            mission.status = MissionStatus.ONGOING
            mission.start_date = datetime.now()
        case "pause":
            if mission.status == MissionStatus.CREATED:
                return err_res(409, "This mission hasn't started yet.")
            if mission.status == MissionStatus.PAUSED:
                return err_res(409, "This mission is already paused.")
            mission.status = MissionStatus.PAUSED
        case "continue":
            if mission.status == MissionStatus.CREATED:
                return err_res(409, "This mission hasn't started yet.")
            if mission.status == MissionStatus.ONGOING:
                return err_res(409, "This mission is already ongoing.")
            mission.status = MissionStatus.ONGOING
        case "cancel":
            if mission.status in ongoing_statues:
                return err_res(409, "You can only end a starting mission.")
            update_lists(
                [str(oid.id) for oid in mission.user_ids], "delete_user", mission
            )
            update_lists([str(oid.id) for oid in mission.device_ids], "delete_device")
            mission.status = MissionStatus.CANCELED
        case "end":
            if mission.status == MissionStatus.CREATED:
                return err_res(409, "You can't end a non-starting mission.")
            update_lists(
                [str(user.id) for user in mission.user_ids], "delete_user", mission
            )
            update_lists(
                [str(device.id) for device in mission.device_ids], "delete_device"
            )
            mission.status = MissionStatus.FINISHED
            mission.end_date = datetime.now()
        case _:
            return err_res(400, "the command provided is invalid.")

    update_cur_mission(mission, "status")
    mission.save()
    data = {
        "message": "mission status is updated successfully.",
        "id": str(mission.id),
        "name": mission.name,
        "status": mission.status.value,
    }
    return jsonify(data), 200
