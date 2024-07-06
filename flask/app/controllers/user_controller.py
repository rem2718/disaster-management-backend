from bson import ObjectId
import os

from mongoengine.queryset.visitor import Q
from flask import jsonify, send_file

from app.models.mission_model import Mission
from app.models.user_model import User
from app.utils.enums import UserStatus
from app.utils.extensions import *
from app.utils.validators import *
from app.utils.mqtt_interface import *

MIN_LENGTH = 3
MAX_LENGTH = 20


@handle_exceptions
def signup(email, password, username):
    null_validator(["Email", "Password", "Username"], [email, password, username])
    existing_user = User.objects(
        (Q(email=email) | Q(username=username)) & Q(status__ne=UserStatus.INACTIVE)
    ).first()
    if existing_user:
        return err_res(409, "Email or Username is already taken.")

    minlength_validator("Username", username, MIN_LENGTH)
    maxlength_validator("Username", username, MAX_LENGTH)
    password_validator(password)

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password=hashed_password, username=username)
    user.save()
    data = {
        "message": "User created successfully. Once you receive approval from the admin, you can access your account and establish a connection with the Cloud MQTT broker using the same credentials.",
    }
    return jsonify(data), 202


@handle_exceptions
def login(email_or_username, password):
    null_validator(["Email or Username", "Password"], [email_or_username, password])

    if User.is_email(email_or_username):
        user = User.objects(
            Q(email=email_or_username) & Q(status__ne=UserStatus.INACTIVE)
        ).first()
    else:
        user = User.objects(
            Q(username=email_or_username) & Q(status__ne=UserStatus.INACTIVE)
        ).first()

    if not user or not user.check_password(password):
        return err_res(401, "Invalid email or password.")

    if user.status == UserStatus.PENDING:
        return err_res(
            403, "Account is pending. Login not allowed until admin approval."
        )
    if user.status == UserStatus.REJECTED:
        return err_res(403, "Account is rejected. Please contact support.")

    if not user.has_mqtt_creds:
        mqtt_client.create_mqtt_user(user.username, password)
        user.has_mqtt_creds = True
        user.save()

    token = user.generate_token()
    data = {
        "message": f"User {user.username} loggedin successfully.",
        "username": user.username,
        "type": user.type.value,
        "token": token,
    }
    return jsonify(data), 200


@handle_exceptions
def rtmp_auth(username, password):
    null_validator(["Username", "Password"], [username, password])

    user = User.objects(
        Q(username=username) & Q(status__ne=UserStatus.INACTIVE)
    ).first()

    if not user or not user.check_password(password):
        return err_res(401, "Invalid username or password.")

    if user.status not in [UserStatus.AVAILABLE, UserStatus.ASSIGNED]:
        return err_res(403, "Account is unavailable. Please contact support.")

    data = {
        "message": f"User {user.username} loggedin successfully.",
    }
    return jsonify(data), 200


@handle_exceptions
def logout(user_id):
    if not user_id:
        return err_res(400, "Invalid token")

    User.objects.get(id=user_id)
    return jsonify({"message": "User logged out successfully.", "token": ""}), 200

@authorize_admin
@handle_exceptions
def upload_embeddings(usertype, file):
    if file.filename == '':
        return err_res(400, "No Pickle file provided.")
    if file and file.filename.endswith('.pkl'):
        file.save("app/static/embeddings.pkl")
        return jsonify({"message": "The Pickle file is uploaded successfully."}), 200
    else:
        return err_res(400, "No Pickle file provided.")

@handle_exceptions
def get_embeddings():
    filepath = "app/static/embeddings.pkl"
    if os.path.exists(filepath):
        file = open(filepath, "rb")
        return send_file(file, as_attachment=True, download_name="embeddings.pkl")
    else:
        return err_res(404, "No Pickle found.")
    
@handle_exceptions
def get_info(user_id):
    if not user_id:
        return err_res(400, "Invalid token")

    user = User.objects.get(id=user_id)
    data = {
        "user_id": str(user.id),
        "email": user.email,
        "username": user.username,
    }
    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def get_user_info(user_type, user_id):
    null_validator(["User ID"], [user_id])
    user = User.objects.get(id=user_id)
    missions = [
        {
            "mission_id": str(mission._id),
            "name": mission.name,
            "status": mission.status.value,
        }
        for mission in user.cur_missions
    ]
    data = {
        "user_id": str(user.id),
        "email": user.email,
        "username": user.username,
        "type": user.type,
        "status": user.status,
        "cur_missions": missions,
    }
    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def get_all(user_type, page_number, page_size, username, statuses, types, mission_id):
    query, items = {}, []

    if username:
        query["username__icontains"] = username

    if statuses:
        query["status__in"] = statuses
    if types:
        query["type__in"] = types
    users = User.objects(**query).paginate(page=page_number, per_page=page_size)

    if mission_id:
        mission_users = []
        mission = Mission.objects.get(id=mission_id)
        for usr in mission.user_ids:
            mission_users.append(str(usr.id))
            user = User.objects.get(id=str(usr.id))
            items.append(
                {
                    "id": str(user.id),
                    "username": user.username,
                    "type": user.type,
                    "status": user.status,
                    "in_mission": True,
                    "active_mission_count": len(user.cur_missions),
                }
            )

        items += [
            {
                "id": str(user.id),
                "username": user.username,
                "type": user.type,
                "status": user.status,
                "in_mission": False,
                "active_mission_count": len(user.cur_missions),
            }
            for user in users.items
            if str(user.id) not in mission_users
        ]
    else:
        items = [
            {
                "id": str(user.id),
                "username": user.username,
                "type": user.type,
                "status": user.status,
                "active_mission_count": len(user.cur_missions),
            }
            for user in users.items
        ]

    data = {
        "items": items,
        "has_next": users.has_next,
        "has_prev": users.has_prev,
        "page": users.page,
        "total_pages": users.pages,
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

    user_count = User.objects(**query).count()

    data = {"status": statuses, "type": types, "count": user_count}

    return jsonify(data), 200


@handle_exceptions
def get_cur_missions(user_id, page_number, page_size, name, statuses):
    if not user_id:
        return err_res(400, "Invalid token")

    user = User.objects.get(id=user_id)
    filtered_missions = user.cur_missions
    if name:
        filtered_missions = [
            mission
            for mission in filtered_missions
            if name.lower() in mission.name.lower()
        ]
    if statuses:
        filtered_missions = [
            mission for mission in filtered_missions if mission.status.value in statuses
        ]

    missions = [
        {
            "mission_id": str(mission._id),
            "name": mission.name,
            "status": mission.status.value,
        }
        for mission in filtered_missions
    ]

    total_missions = len(missions)
    total_pages = (total_missions + page_size - 1) // page_size
    start = (page_number - 1) * page_size
    end = start + page_size
    paginated_missions = missions[start:end]
    data = {
        "items": paginated_missions,
        "cur_missions_count": total_missions,
        "has_next": page_number < total_pages,
        "has_prev": page_number > 1,
        "page": page_number,
        "total_pages": total_pages,
    }
    return jsonify(data), 200


@authorize_admin
@handle_exceptions
def user_approval(user_type, user_id, approved, type):
    null_validator(["Approved"], [approved])
    user = User.objects.get(id=user_id)

    if user.status not in [UserStatus.PENDING, UserStatus.REJECTED]:
        return err_res(409, "User account is not pending.")

    if approved:
        enum_validator("UserType", type, UserType)
        user.status = UserStatus.AVAILABLE
        user.type = type
    else:
        user.status = UserStatus.REJECTED

    user.save()
    data = {"message": "User account status is updated successfully."}
    return jsonify(data), 200


@handle_exceptions
def update_info(user_id, username, email, password):
    if not user_id:
        return err_res(400, "Invalid token")

    user = User.objects.get(id=user_id)
    if user.check_password(password):
        return err_res(401, "Invalid password.")

    if username:
        if user.username != username:
            existing_user = User.objects(username=username).first()
            if existing_user:
                return err_res(409, "Username is already taken.")
        else:
            return err_res(
                409, "The username provided is identical to the current one."
            )

        minlength_validator("Username", username, MIN_LENGTH)
        maxlength_validator("Username", username, MAX_LENGTH)
        user.username = username
        mqtt_client.delete_mqtt_user(user.username)
        mqtt_client.create_mqtt_user(user.username, password)

    if email:
        if user.email != email:
            existing_user = User.objects(email=email).first()
            if existing_user:
                return err_res(409, "Email is already taken.")
        else:
            return err_res(409, "The email provided is identical to the current one.")
        user.email = email

    user.save()
    data = {
        "message": "User information is updated successfully.",
        "email": user.email,
        "username": user.username,
    }
    return jsonify(data), 200


@handle_exceptions
def update_password(user_id, old_password, new_password):
    if not user_id:
        return err_res(400, "Invalid token")

    null_validator(["Old password", "New password"], [old_password, new_password])

    if old_password == new_password:
        return err_res(409, "The new password is identical to the current one.")

    user = User.objects.get(id=user_id)

    if not user.check_password(old_password):
        return err_res(401, "Incorrect old password try again.")

    password_validator(new_password)

    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    mqtt_client.delete_mqtt_user(user.username)
    mqtt_client.create_mqtt_user(user.username, new_password)
    user.save()
    return jsonify({"message": "Password is updated successfully."}), 200


@authorize_admin
@handle_exceptions
def update_admin_info(user_type, user_id, email, type):
    user = User.objects.get(id=user_id)

    if user.status in [UserStatus.PENDING, UserStatus.INACTIVE, UserStatus.REJECTED]:
        return err_res(409, "You can't update this user information.")

    if email:
        if user.email != email:
            existing_user = User.objects(email=email).first()
            if existing_user:
                return err_res(409, "Email is already taken.")
        else:
            return err_res(409, "The email provided is identical to the current one.")
        user.email = email

    if type:
        enum_validator("UserType", type, UserType)
        user.type = type

    user.save()
    data = {
        "message": "User information is updated successfully.",
        "email": user.email,
        "type": user.type,
    }
    return jsonify(data), 200


@handle_exceptions
def update_password(user_id, old_password, new_password):
    if not user_id:
        return err_res(400, "Invalid token")

    null_validator(["Old password", "New password"], [old_password, new_password])

    if old_password == new_password:
        return err_res(409, "The new password is identical to the current one.")

    user = User.objects.get(id=user_id)

    if not user.check_password(old_password):
        return err_res(401, "Incorrect old password try again.")

    password_validator(new_password)

    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    mqtt_client.delete_mqtt_user(user.username)
    mqtt_client.create_mqtt_user(user.username, new_password)
    user.save()
    return jsonify({"message": "Password is updated successfully."}), 200


@authorize_admin
@handle_exceptions
def delete_user(user_type, user_id):
    user = User.objects.get(id=user_id)
    if user.status == UserStatus.PENDING:
        return err_res(409, "Pending users can't be deactivated.")

    if user.status in [UserStatus.INACTIVE, UserStatus.REJECTED]:
        return err_res(409, "User is already Inactive.")

    for mission in user.cur_missions:
        Mission.objects(id=mission._id).update_one(pull__user_ids=ObjectId(user_id))

    User.objects(id=user_id).update(
        set__cur_missions=[], set__status=UserStatus.INACTIVE, set__has_mqtt_creds=False
    )

    mqtt_client.delete_mqtt_user(user.username)
    return jsonify({"message": "User is deleted successfully."}), 200
