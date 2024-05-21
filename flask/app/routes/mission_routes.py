from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request

from app.controllers.mission_controller import *

mission = Blueprint("mission_routes", __name__, url_prefix="/api/missions")

DEF_PAGE_NUM = 1
DEF_PAGE_SIZE = 5

# TO-DO: notify brokers/ robots when mission start or end


@mission.route("/", methods=["POST"])
@jwt_required()
def create_route():
    user_type = get_jwt_identity()["type"]
    name = request.json.get("name", None)
    device_ids = request.json.get("device_ids", None)
    user_ids = request.json.get("user_ids", None)
    return create(user_type, name, device_ids, user_ids)


@mission.route("/<mission_id>", methods=["GET"])
@jwt_required()
def get_info_route(mission_id):
    user_type = get_jwt_identity()["type"]
    return get_info(user_type, mission_id)


@mission.route("/all", methods=["GET"])
@jwt_required()
def get_all_route():
    user_type = get_jwt_identity()["type"]
    page_number = int(request.args.get("page-number", DEF_PAGE_NUM))
    page_size = int(request.args.get("page-size", DEF_PAGE_SIZE))
    name = request.args.get("name", None)

    status_list = request.args.getlist("status")
    statuses = list(map(int, status_list)) if status_list else None

    return get_all(user_type, page_number, page_size, name, statuses)


@mission.route("/count", methods=["GET"])
@jwt_required()
def get_count_route():
    user_type = get_jwt_identity()["type"]

    status_list = request.args.getlist("status")
    statuses = list(map(int, status_list)) if status_list else None

    return get_count(user_type, statuses)


@mission.route("/<mission_id>", methods=["PUT"])
@jwt_required()
def update_route(mission_id):
    user_type = get_jwt_identity()["type"]
    name = request.json.get("name", None)
    device_ids = request.json.get("device_ids", None)
    user_ids = request.json.get("user_ids", None)
    return update(user_type, mission_id, name, device_ids, user_ids)


@mission.route("/<mission_id>/<command>", methods=["PUT"])
@jwt_required()
def status_route(mission_id, command):
    user_type = get_jwt_identity()["type"]
    return change_status(user_type, mission_id, command)
