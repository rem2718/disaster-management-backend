from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request

from app.controllers.device_controller import *

DEF_PAGE_NUM = 1
DEF_PAGE_SIZE = 5

device = Blueprint("device_routes", __name__, url_prefix="/api/devices")


@device.route("/", methods=["POST"])
@jwt_required()
def register_route():
    user_type = get_jwt_identity()["type"]
    name = request.json.get("name", None)
    password = request.json.get("password", None)
    mac = request.json.get("mac", None)
    type = request.json.get("type", None)
    broker_id = request.json.get("broker_id", None)
    return register(user_type, name, password, mac, type, broker_id)


@device.route("/rtmp_auth", methods=["GET"])
def rtmp_auth_route():
    name = request.args.get("name", None)
    password = request.args.get("password", None)
    return rtmp_auth(name, password)


@device.route("/<device_id>", methods=["GET"])
@jwt_required()
def get_info_route(device_id):
    user_type = get_jwt_identity()["type"]
    return get_info(user_type, device_id)


@device.route("/all", methods=["GET"])
@jwt_required()
def get_all_route():
    user_type = get_jwt_identity()["type"]
    page_number = int(request.args.get("page-number", DEF_PAGE_NUM))
    page_size = int(request.args.get("page-size", DEF_PAGE_SIZE))
    name = request.args.get("name", None)

    status_list = request.args.getlist("status")
    statuses = list(map(int, status_list)) if status_list else None

    type_list = request.args.getlist("type")
    types = list(map(int, type_list)) if type_list else None

    mission = request.args.get("mission")
    mission_id = request.args.get("mission") if mission else None
    return get_all(user_type, page_number, page_size, name, statuses, types, mission_id)


@device.route("/count", methods=["GET"])
@jwt_required()
def get_count_route():
    user_type = get_jwt_identity()["type"]

    status_list = request.args.getlist("status")
    statuses = list(map(int, status_list)) if status_list else None

    type_list = request.args.getlist("type")
    types = list(map(int, type_list)) if type_list else None

    return get_count(user_type, statuses, types)


@device.route("broker_id", methods=["GET"])
@jwt_required()
def get_broker_id_route():
    user_type = get_jwt_identity()["type"]
    mac = request.args.get("mac", None)
    return get_broker_id(user_type, mac)


@device.route("/<device_id>", methods=["PUT"])
@jwt_required()
def update_route(device_id):
    user_type = get_jwt_identity()["type"]
    name = request.json.get("name", None)
    old_password = request.json.get("old_password", None)
    new_password = request.json.get("new_password", None)

    return update(user_type, device_id, name, old_password, new_password)


@device.route("/<device_id>/state", methods=["PUT"])
@jwt_required()
def update_state_route(device_id):
    state = request.json.get("state", None)
    return update_state(device_id, state)


@device.route("/broker", methods=["PUT"])
@jwt_required()
def update_broker_route():
    user_type = get_jwt_identity()["type"]
    name = request.json.get("name", None)
    broker_mac = request.json.get("broker_mac", None)
    return update_broker(user_type, name, broker_mac)


@device.route("/<device_id>", methods=["DELETE"])
@jwt_required()
def deactivate_route(device_id):
    user_type = get_jwt_identity()["type"]
    return deactivate(user_type, device_id)
