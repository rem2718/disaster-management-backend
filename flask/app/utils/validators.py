from bson import ObjectId
import re

from mongoengine.errors import ValidationError, DoesNotExist
from mongoengine.queryset.visitor import Q

from app.utils.enums import UserStatus, DeviceStatus, DeviceType
from app.models.device_model import Device
from app.models.user_model import User


def null_validator(fields, values):
    for field, value in zip(fields, values):
        if value == None:
            raise ValidationError(f"{field} is required")


def minlength_validator(field, value, limit):
    if len(value) < limit:
        raise ValidationError(
            f"The length of '{field}' must be at least {limit} characters."
        )


def maxlength_validator(field, value, limit):
    if len(value) > limit:
        raise ValidationError(
            f"The length of '{field}' must be at most {limit} characters."
        )


def password_validator(password):
    if (
        len(password) < 8
        or not any(char.isupper() for char in password)
        or not any(char.islower() for char in password)
        or not any(char.isdigit() for char in password)
        or not any(char in "!@#$%^&*()-_+=<>,.?/:;{}[]~" for char in password)
    ):
        raise ValidationError(
            "Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character."
        )


def mac_validator(mac):
    mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    if not mac_pattern.match(mac):
        raise ValidationError("The MAC address provided is not valid")


def enum_validator(enum_name, value, enum):
    if value not in [member.value for member in enum]:
        raise ValidationError(f"{value} is not a valid {enum_name} type")


def device_validator(device_ids):
    existing_devices = Device.objects(
        Q(id__in=device_ids)
        & Q(status=DeviceStatus.AVAILABLE)
        & Q(type__en=DeviceType.BROKER)
    )
    existing_set = set(str(device.id) for device in existing_devices)
    provided_set = set(device_ids)
    missing_devices = provided_set - existing_set
    if missing_devices:
        raise DoesNotExist(
            f"Invalid device IDs: {', '.join(str(dev_id) for dev_id in missing_devices)}"
        )


def user_validator(user_ids):
    existing_users = User.objects(
        Q(id__in=user_ids)
        & (Q(status=UserStatus.AVAILABLE) | Q(status=UserStatus.ASSIGNED))
    )
    missing_users = set(user_ids) - set(user.id for user in existing_users)
    existing_set = set(str(user.id) for user in existing_users)
    provided_set = set(user_ids)
    missing_users = provided_set - existing_set
    if missing_users:
        raise DoesNotExist(
            f"Invalid user IDs: {', '.join(str(user_id) for user_id in missing_users)}"
        )


def broker_validator(broker_id):
    existing_broker = Device.objects(
        Q(id=ObjectId(broker_id))
        & Q(type=DeviceType.BROKER)
        & Q(status__ne=DeviceStatus.INACTIVE)
    )
    if not existing_broker:
        raise DoesNotExist(f"Invalid broker ID: {broker_id}")
