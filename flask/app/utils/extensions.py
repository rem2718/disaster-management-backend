from functools import wraps

from mongoengine.errors import DoesNotExist, ValidationError
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask import jsonify

from app.utils.enums import UserType

db = MongoEngine()
bcrypt = Bcrypt()
jwt = JWTManager()

def err_res(code, data):
    match code:
        case 400:
            err = "Bad Request Error"
        case 401:
            err = "Unauthorized Error"
        case 403:
            err = "Forbidden Error"
        case 404:
            err = "Not Found Error"
        case 409:
            err = "Conflict Error"
        case 500:
            err = "Internal Server Error"

    return jsonify({"error": err, "message": data}), code


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as ve:
            return err_res(400, str(ve))
        except DoesNotExist as dne:
            return err_res(404, str(dne))
        except Exception as e:
            return err_res(500, str(e))

    return wrapper


def authorize_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_type = args[0]
        if user_type != UserType.ADMIN.value:
            return err_res(403, "Admin access is required.")
        else:
            return func(*args, **kwargs)

    return wrapper
