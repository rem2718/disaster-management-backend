from app.utils.enums import DeviceType, DeviceStatus
from app.utils.extensions import db, bcrypt


class Device(db.Document):
    name = db.StringField(required=True)
    password = db.StringField(required=True)
    mac = db.StringField(required=True)
    type = db.EnumField(DeviceType, default=DeviceType.UGV)
    status = db.EnumField(DeviceStatus, default=DeviceStatus.AVAILABLE)
    broker_id = db.ReferenceField("self", default=None)
    meta = {"collection": "Devices"}

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return (
            f"<Device:\n"
            f"id: {str(self.id)}\n"
            f"name: {self.name}\n"
            f"mac: {self.mac}\n"
            f"status: {DeviceStatus(self.status).name}\n"
            f"type: {DeviceType(self.type).name}\n"
            f"broker_id: {str(self.broker_id)}"
        )
